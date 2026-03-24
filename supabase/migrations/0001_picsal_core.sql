create extension if not exists "pgcrypto";

create table if not exists public.user_profiles (
    id uuid primary key references auth.users (id) on delete cascade,
    email text not null unique,
    display_name text not null default '',
    avatar_path text not null default '',
    role text not null default 'user' check (role in ('user', 'admin', 'superuser')),
    metadata jsonb not null default '{}'::jsonb,
    last_login_at timestamptz,
    created_at timestamptz not null default timezone('utc', now()),
    updated_at timestamptz not null default timezone('utc', now())
);

create or replace function public.set_updated_at()
returns trigger
language plpgsql
as $$
begin
    new.updated_at = timezone('utc', now());
    return new;
end;
$$;

drop trigger if exists trg_user_profiles_updated_at on public.user_profiles;
create trigger trg_user_profiles_updated_at
before update on public.user_profiles
for each row
execute function public.set_updated_at();

create or replace function public.current_picsal_role()
returns text
language sql
stable
as $$
    select coalesce(auth.jwt() -> 'app_metadata' ->> 'picsal_role', 'user');
$$;

alter table public.user_profiles enable row level security;

drop policy if exists "Admins and superusers can view all profiles" on public.user_profiles;
create policy "Admins and superusers can view all profiles"
on public.user_profiles
for select
to authenticated
using (
    public.current_picsal_role() in ('admin', 'superuser')
    or auth.uid() = id
);

drop policy if exists "Users can update their own profile" on public.user_profiles;
create policy "Users can update their own profile"
on public.user_profiles
for update
to authenticated
using (
    public.current_picsal_role() in ('admin', 'superuser')
    or auth.uid() = id
)
with check (
    public.current_picsal_role() in ('admin', 'superuser')
    or auth.uid() = id
);

drop policy if exists "Admins and superusers can insert profiles" on public.user_profiles;
create policy "Admins and superusers can insert profiles"
on public.user_profiles
for insert
to authenticated
with check (
    public.current_picsal_role() in ('admin', 'superuser')
);

drop policy if exists "Admins and superusers can delete profiles" on public.user_profiles;
create policy "Admins and superusers can delete profiles"
on public.user_profiles
for delete
to authenticated
using (
    public.current_picsal_role() in ('admin', 'superuser')
);
