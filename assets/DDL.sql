--drop table public.user;

create TABLE public.USER (
  id_inst INT PRIMARY KEY,
  city VARCHAR(50),
  inverter VARCHAR(100),
  power INT
);