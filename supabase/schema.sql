-- Run this SQL in the Supabase SQL Editor before enabling profile storage.
-- The id is the authenticated user's UUID; RLS ensures users only access their own row.

create table if not exists public.student_profiles (
    id uuid primary key references auth.users (id) on delete cascade,
    profile jsonb not null default '{}'::jsonb,
    updated_at timestamptz not null default now()
);

alter table public.student_profiles enable row level security;

drop policy if exists "Learners can read their own profile" on public.student_profiles;
create policy "Learners can read their own profile"
on public.student_profiles for select
to authenticated
using ((select auth.uid()) = id);

drop policy if exists "Learners can insert their own profile" on public.student_profiles;
create policy "Learners can insert their own profile"
on public.student_profiles for insert
to authenticated
with check ((select auth.uid()) = id);

drop policy if exists "Learners can update their own profile" on public.student_profiles;
create policy "Learners can update their own profile"
on public.student_profiles for update
to authenticated
using ((select auth.uid()) = id)
with check ((select auth.uid()) = id);

drop policy if exists "Learners can delete their own profile" on public.student_profiles;
create policy "Learners can delete their own profile"
on public.student_profiles for delete
to authenticated
using ((select auth.uid()) = id);

grant select, insert, update, delete on public.student_profiles to authenticated;
