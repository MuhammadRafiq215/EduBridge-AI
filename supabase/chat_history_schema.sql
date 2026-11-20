-- Phase 7: optional persistent AI Teacher conversation history.
-- Run only after confirming the project's Supabase account and data terms are suitable.
-- Raw chat storage is OFF by default in the app and requires an explicit learner opt-in.
-- Users can view their own history and delete it from the AI Teacher workspace.

create table if not exists public.student_chat_history (
    user_id uuid primary key references auth.users (id) on delete cascade,
    messages jsonb not null default '[]'::jsonb,
    updated_at timestamptz not null default now(),
    constraint student_chat_history_messages_is_array
        check (jsonb_typeof(messages) = 'array')
);

alter table public.student_chat_history enable row level security;

drop policy if exists "Learners can read their own chat history" on public.student_chat_history;
create policy "Learners can read their own chat history"
on public.student_chat_history for select
to authenticated
using ((select auth.uid()) = user_id);

drop policy if exists "Learners can insert their own chat history" on public.student_chat_history;
create policy "Learners can insert their own chat history"
on public.student_chat_history for insert
to authenticated
with check ((select auth.uid()) = user_id);

drop policy if exists "Learners can update their own chat history" on public.student_chat_history;
create policy "Learners can update their own chat history"
on public.student_chat_history for update
to authenticated
using ((select auth.uid()) = user_id)
with check ((select auth.uid()) = user_id);

drop policy if exists "Learners can delete their own chat history" on public.student_chat_history;
create policy "Learners can delete their own chat history"
on public.student_chat_history for delete
to authenticated
using ((select auth.uid()) = user_id);

grant select, insert, update, delete on public.student_chat_history to authenticated;
