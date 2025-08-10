-- Adds optional fields for storing avatar URL and full name
-- Also ensures indexes/policies are compatible

begin;

-- Add columns if they do not exist
alter table if exists public.user_profiles
  add column if not exists avatar_url text,
  add column if not exists full_name text;

-- Helpful index for frequent lookups by user_id
create index if not exists idx_user_profiles_user_id on public.user_profiles(user_id);

commit;

