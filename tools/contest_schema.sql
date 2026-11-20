-- Seeded · concours « Battez le modèle » (point 15a, règle « bonus outsider »)
-- À coller une seule fois dans Supabase > SQL Editor > New query, puis « Run ».
-- Le navigateur des visiteurs ne touche jamais aux tables directement : il passe par des fonctions
-- (set_pseudo, submit_pick, my_picks, match_picks, player_picks, leaderboard) qui vérifient tout côté serveur.
-- On peut relancer ce fichier sans risque : il ne détruit rien.
-- Le robot GitHub (clé secrète) remplit les matchs et les résultats.

-- 1) Matchs du concours (écrits par le robot)
create table if not exists contest_matches (
  id         text primary key,                 -- ex. « atp-2027-australian-open-sinner-popyrin »
  circuit    text not null check (circuit in ('atp', 'wta')),
  tourney    text not null,
  a          text not null,
  b          text not null,
  starts_at  timestamptz not null,             -- heure de début : les pronostics se ferment à ce moment-là
  seeded_pa  real check (seeded_pa between 0 and 1),   -- proba Seeded que « a » gagne, figée avant le match
  winner     text check (winner in ('a', 'b')),
  void       boolean not null default false    -- forfait / match annulé : ne compte pas
);

-- 2) Joueurs du concours : un identifiant aléatoire gardé dans le navigateur + un pseudo unique
create table if not exists contest_players (
  player_id  uuid primary key,
  pseudo     text not null unique check (char_length(pseudo) between 3 and 20 and pseudo ~ '^[A-Za-z0-9_.-]+$'),
  created_at timestamptz not null default now()
);

-- 3) Pronostics (un par joueur et par match, modifiable jusqu'au début du match)
create table if not exists contest_picks (
  match_id   text not null references contest_matches(id) on delete cascade,
  player_id  uuid not null references contest_players(player_id) on delete cascade,
  pa         real not null check (pa between 0 and 1),   -- choix : 1 = « a », 0 = « b »
  updated_at timestamptz not null default now(),
  primary key (match_id, player_id)
);

-- Personne n'accède aux tables directement depuis le navigateur
alter table contest_matches enable row level security;
alter table contest_players enable row level security;
alter table contest_picks   enable row level security;
-- les matchs, eux, peuvent être lus par tout le monde (liste du concours)
drop policy if exists "matchs lisibles" on contest_matches;
create policy "matchs lisibles" on contest_matches for select to anon, authenticated using (true);
grant select on contest_matches to anon, authenticated;

-- Règle « bonus outsider » (choix de Cyrus, 20/11) : on choisit le vainqueur (pa = 1 → « a », pa = 0 → « b »).
-- Bon choix = 10 ÷ (chance que Seeded donnait à ce joueur), arrondi, 100 au maximum ; mauvais choix = 0.
-- Ex. favori à 80 % → 13 pts ; outsider à 20 % → 50 pts ; 10 % ou moins → 100 pts.
create or replace function contest_points(p_pa real, p_winner text, p_seeded real) returns real
language sql immutable as $$
  select case when (p_pa >= 0.5) = (p_winner = 'a')
              then round(10 / greatest(0.1, round((case when p_pa >= 0.5 then coalesce(p_seeded, 0.5) else 1 - coalesce(p_seeded, 0.5) end)::numeric, 4)))
              else 0 end::real
$$;

-- Choisir / changer son pseudo
create or replace function set_pseudo(p_player uuid, p_pseudo text) returns text
language plpgsql security definer set search_path = public as $$
begin
  if lower(p_pseudo) like '%seeded%' then raise exception 'pseudo_reserve'; end if;   -- « Seeded » = le modèle
  insert into contest_players(player_id, pseudo) values (p_player, p_pseudo)
  on conflict (player_id) do update set pseudo = excluded.pseudo;
  return p_pseudo;
exception when unique_violation then
  raise exception 'pseudo_pris';
end $$;

-- Envoyer un pronostic : refusé si le match a commencé (heure du serveur, pas celle du visiteur)
create or replace function submit_pick(p_player uuid, p_match text, p_pa real) returns void
language plpgsql security definer set search_path = public as $$
begin
  if not exists (select 1 from contest_players where player_id = p_player) then raise exception 'pas_de_pseudo'; end if;
  if not exists (select 1 from contest_matches where id = p_match and starts_at > now() and not void) then raise exception 'match_ferme'; end if;
  if p_pa not in (0, 1) then raise exception 'choix_invalide'; end if;
  insert into contest_picks(match_id, player_id, pa) values (p_match, p_player, p_pa)
  on conflict (match_id, player_id) do update set pa = excluded.pa, updated_at = now();
end $$;

-- Mes pronostics (pour les réafficher dans la page)
create or replace function my_picks(p_player uuid)
returns table(match_id text, pa real, points real)
language sql stable security definer set search_path = public as $$
  select p.match_id, p.pa, case when m.winner is not null and not m.void then contest_points(p.pa, m.winner, m.seeded_pa) end
  from contest_picks p join contest_matches m on m.id = p.match_id where p.player_id = p_player
$$;

-- Pronostics des autres, façon Mon Petit Prono : visibles par tout le monde, mais SEULEMENT une fois le match
-- commencé (avant, personne ne peut copier). Renvoie aussi les points une fois le résultat connu.
create or replace function match_picks(p_match text)
returns table(pseudo text, pa real, points real)
language sql stable security definer set search_path = public as $$
  select pl.pseudo, p.pa, case when m.winner is not null and not m.void then contest_points(p.pa, m.winner, m.seeded_pa) end
  from contest_picks p join contest_matches m on m.id = p.match_id join contest_players pl on pl.player_id = p.player_id
  where p.match_id = p_match and m.starts_at <= now()
  order by pl.pseudo
$$;

-- Fiche d'un joueur du concours : tous ses pronostics des matchs déjà commencés
create or replace function player_picks(p_pseudo text)
returns table(match_id text, tourney text, a text, b text, starts_at timestamptz, pa real, points real)
language sql stable security definer set search_path = public as $$
  select m.id, m.tourney, m.a, m.b, m.starts_at, p.pa, case when m.winner is not null and not m.void then contest_points(p.pa, m.winner, m.seeded_pa) end
  from contest_picks p join contest_matches m on m.id = p.match_id join contest_players pl on pl.player_id = p.player_id
  where pl.pseudo = p_pseudo and m.starts_at <= now()
  order by m.starts_at desc
$$;

-- Classement : total des points sur les matchs terminés (Seeded joue toujours son favori)
drop function if exists leaderboard(text);
create or replace function leaderboard(p_circuit text default null)
returns table(pseudo text, n bigint, total real, is_model boolean)
language sql stable security definer set search_path = public as $$
  select pl.pseudo, count(*), sum(contest_points(p.pa, m.winner, m.seeded_pa))::real, false
  from contest_picks p join contest_matches m on m.id = p.match_id join contest_players pl on pl.player_id = p.player_id
  where m.winner is not null and not m.void and (p_circuit is null or m.circuit = p_circuit)
  group by pl.pseudo
  union all
  select 'Seeded', count(*), sum(contest_points(case when m.seeded_pa >= 0.5 then 1 else 0 end, m.winner, m.seeded_pa))::real, true
  from contest_matches m
  where m.winner is not null and not m.void and m.seeded_pa is not null and (p_circuit is null or m.circuit = p_circuit)
  having count(*) > 0
  order by 3 desc
$$;

revoke all on function set_pseudo(uuid, text), submit_pick(uuid, text, real), my_picks(uuid), match_picks(text), player_picks(text), leaderboard(text) from public;
grant execute on function set_pseudo(uuid, text), submit_pick(uuid, text, real), my_picks(uuid), match_picks(text), player_picks(text), leaderboard(text) to anon, authenticated;

-- l'ancienne règle (pourcentages) n'est plus utilisée
drop function if exists contest_points(real, text);
