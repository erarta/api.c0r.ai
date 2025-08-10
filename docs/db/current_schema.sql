-- WARNING: This schema is for context only and is not meant to be run.
-- Table order and constraints may not be valid for execution.

CREATE TABLE public.daily_calories (
  user_id uuid NOT NULL,
  date date NOT NULL,
  id uuid NOT NULL DEFAULT gen_random_uuid(),
  total_calories numeric DEFAULT 0,
  total_proteins numeric DEFAULT 0,
  total_fats numeric DEFAULT 0,
  total_carbohydrates numeric DEFAULT 0,
  created_at timestamp with time zone DEFAULT now(),
  updated_at timestamp with time zone DEFAULT now(),
  CONSTRAINT daily_calories_pkey PRIMARY KEY (id),
  CONSTRAINT daily_calories_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id)
);
CREATE TABLE public.logs (
  action_type text DEFAULT 'photo_analysis'::text,
  metadata jsonb DEFAULT '{}'::jsonb,
  user_id uuid,
  photo_url text,
  kbzhu jsonb,
  model_used text,
  id uuid NOT NULL DEFAULT gen_random_uuid(),
  timestamp timestamp with time zone DEFAULT now(),
  CONSTRAINT logs_pkey PRIMARY KEY (id),
  CONSTRAINT logs_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id)
);
CREATE TABLE public.payments (
  user_id uuid,
  amount numeric NOT NULL,
  gateway text NOT NULL,
  status text,
  id uuid NOT NULL DEFAULT gen_random_uuid(),
  timestamp timestamp with time zone DEFAULT now(),
  CONSTRAINT payments_pkey PRIMARY KEY (id),
  CONSTRAINT payments_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id)
);
CREATE TABLE public.schema_migrations (
  filename character varying NOT NULL UNIQUE,
  rollback_filename character varying,
  checksum character varying,
  id integer NOT NULL DEFAULT nextval('schema_migrations_id_seq'::regclass),
  applied_at timestamp without time zone DEFAULT now(),
  status character varying DEFAULT 'applied'::character varying,
  created_at timestamp without time zone DEFAULT now(),
  updated_at timestamp without time zone DEFAULT now(),
  CONSTRAINT schema_migrations_pkey PRIMARY KEY (id)
);
CREATE TABLE public.user_profiles (
  user_id uuid NOT NULL UNIQUE,
  daily_calories_target integer,
  age integer NOT NULL CHECK (age >= 10 AND age <= 120),
  gender text NOT NULL CHECK (gender = ANY (ARRAY['male'::text, 'female'::text])),
  height_cm integer NOT NULL CHECK (height_cm >= 100 AND height_cm <= 250),
  id uuid NOT NULL DEFAULT gen_random_uuid(),
  created_at timestamp with time zone DEFAULT now(),
  updated_at timestamp with time zone DEFAULT now(),
  weight_kg numeric NOT NULL CHECK (weight_kg >= 30::numeric AND weight_kg <= 300::numeric),
  activity_level text NOT NULL CHECK (activity_level = ANY (ARRAY['sedentary'::text, 'lightly_active'::text, 'moderately_active'::text, 'very_active'::text, 'extremely_active'::text])),
  goal text NOT NULL CHECK (goal = ANY (ARRAY['lose_weight'::text, 'maintain_weight'::text, 'gain_weight'::text])),
  dietary_preferences ARRAY DEFAULT '{}'::text[] CHECK (dietary_preferences <@ ARRAY['vegetarian'::text, 'vegan'::text, 'pescatarian'::text, 'keto'::text, 'paleo'::text, 'mediterranean'::text, 'low_carb'::text, 'low_fat'::text, 'gluten_free'::text, 'dairy_free'::text, 'halal'::text, 'kosher'::text, 'none'::text]),
  allergies ARRAY DEFAULT '{}'::text[] CHECK (allergies <@ ARRAY['nuts'::text, 'peanuts'::text, 'shellfish'::text, 'fish'::text, 'eggs'::text, 'dairy'::text, 'soy'::text, 'wheat'::text, 'gluten'::text, 'sesame'::text, 'sulfites'::text, 'none'::text]),
  CONSTRAINT user_profiles_pkey PRIMARY KEY (id),
  CONSTRAINT user_profiles_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id)
);
CREATE TABLE public.users (
  language text DEFAULT 'en'::text CHECK (language = ANY (ARRAY['en'::text, 'ru'::text])),
  country text,
  phone_number text,
  telegram_id bigint NOT NULL UNIQUE,
  id uuid NOT NULL DEFAULT gen_random_uuid(),
  credits_remaining integer NOT NULL DEFAULT 3,
  total_paid numeric NOT NULL DEFAULT 0,
  created_at timestamp with time zone DEFAULT now(),
  CONSTRAINT users_pkey PRIMARY KEY (id)
);