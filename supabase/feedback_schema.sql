-- Optional anonymous feedback inbox for the student pilot.
-- Separate from student_profiles; this does not alter existing profile data or policies.
-- Run once in Supabase SQL Editor before enabling the in-app feedback form.

create table if not exists public.student_feedback (
    id uuid primary key default gen_random_uuid(),
    category text not null check (category in ('Bug or error','Confusing instructions','Design or navigation','Feature idea','Something I liked','Other')),
    workspace text not null check (workspace in ('Dashboard','My learning profile','Career pathways','Study planner','Research insights','Account & privacy','About EduBridge','Overall experience')),
    rating smallint not null check (rating between 1 and 5),
    message text not null check (char_length(btrim(message)) between 10 and 1000),
    created_at timestamptz not null default now()
);

alter table public.student_feedback enable row level security;
drop policy if exists "Anyone can submit pilot feedback" on public.student_feedback;
create policy "Anyone can submit pilot feedback" on public.student_feedback for insert to anon, authenticated
with check (
    category in ('Bug or error','Confusing instructions','Design or navigation','Feature idea','Something I liked','Other')
    and workspace in ('Dashboard','My learning profile','Career pathways','Study planner','Research insights','Account & privacy','About EduBridge','Overall experience')
    and rating between 1 and 5
    and char_length(btrim(message)) between 10 and 1000
);
revoke all on public.student_feedback from anon, authenticated;
grant insert on public.student_feedback to anon, authenticated;

-- Project owner review query (run in Supabase SQL Editor):
-- select created_at, workspace, category, rating, message
-- from public.student_feedback order by created_at desc;
