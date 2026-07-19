# CHANGELOG

<!-- version list -->

## v1.16.1 (2026-07-19)

### Bug Fixes

- **db**: Remove stray French-slug specialties + backfill canonical darija
  ([#40](https://github.com/mks-zakaria/sehaty-db/pull/40),
  [`a3f527a`](https://github.com/mks-zakaria/sehaty-db/commit/a3f527a8b1cc8473efd0547c3516717159716773))


## v1.16.0 (2026-07-19)

### Features

- **db**: Darija specialty label + starter provider types
  ([#38](https://github.com/mks-zakaria/sehaty-db/pull/38),
  [`064734b`](https://github.com/mks-zakaria/sehaty-db/commit/064734b4192ea677f9fa226e22a8d8045469f9d6))


## v1.15.1 (2026-07-19)

### Bug Fixes

- **db**: Re-export PharmacyStock from sehaty.db
  ([#36](https://github.com/mks-zakaria/sehaty-db/pull/36),
  [`2a4f043`](https://github.com/mks-zakaria/sehaty-db/commit/2a4f043a4d8ac2e8aa8d790fdefcb313a07502da))


## v1.15.0 (2026-07-19)

### Features

- **db**: Add PHARMACY user role ([#34](https://github.com/mks-zakaria/sehaty-db/pull/34),
  [`970c262`](https://github.com/mks-zakaria/sehaty-db/commit/970c262a50864456fee6f03af408c30ccdecbe4c))


## v1.14.0 (2026-07-19)

### Features

- **db**: Cabinets, cabinet sessions, and appointment consultation record
  ([#32](https://github.com/mks-zakaria/sehaty-db/pull/32),
  [`c922566`](https://github.com/mks-zakaria/sehaty-db/commit/c922566a492e2a518796fe6c75aca0bc689db5ed))


## v1.13.0 (2026-07-16)

### Features

- Add messaging threads and messages schema
  ([#30](https://github.com/mks-zakaria/sehaty-db/pull/30),
  [`cf1ac06`](https://github.com/mks-zakaria/sehaty-db/commit/cf1ac069addff36dae7b1356ac841b5f09b71003))


## v1.12.0 (2026-07-15)

### Features

- Add prescription templates (reusable doctor presets)
  ([#28](https://github.com/mks-zakaria/sehaty-db/pull/28),
  [`60e0f1e`](https://github.com/mks-zakaria/sehaty-db/commit/60e0f1eca8fba60161578bd36012781640a6faf3))


## v1.11.0 (2026-07-15)

### Features

- Add reminder_sent_at to appointments ([#26](https://github.com/mks-zakaria/sehaty-db/pull/26),
  [`c01a3ae`](https://github.com/mks-zakaria/sehaty-db/commit/c01a3ae393c8a337bae91d5d0a213cd3f30c419b))


## v1.10.0 (2026-07-15)

### Features

- Add exclusion constraint preventing overlapping active appointments
  ([#24](https://github.com/mks-zakaria/sehaty-db/pull/24),
  [`d824145`](https://github.com/mks-zakaria/sehaty-db/commit/d8241452fe5d11c97c2ca90a23dda3d0d535bf1b))


## v1.9.0 (2026-07-15)

### Features

- Add doctor timezone and availability exceptions
  ([#22](https://github.com/mks-zakaria/sehaty-db/pull/22),
  [`5475cf0`](https://github.com/mks-zakaria/sehaty-db/commit/5475cf0921351c173699b387356b26bd93538069))


## v1.8.0 (2026-07-15)

### Features

- Add ASSISTANT role and doctor-assistant membership
  ([#20](https://github.com/mks-zakaria/sehaty-db/pull/20),
  [`f654b5a`](https://github.com/mks-zakaria/sehaty-db/commit/f654b5acf40fa81aacd638e3706bfc828cc03005))


## v1.7.0 (2026-07-15)

### Features

- Link prescriptions to clinic patients (support walk-ins)
  ([#18](https://github.com/mks-zakaria/sehaty-db/pull/18),
  [`aa23d50`](https://github.com/mks-zakaria/sehaty-db/commit/aa23d508f8c9ddd2207374c60e958483b7da4bd2))


## v1.6.0 (2026-07-15)

### Features

- Add diagnoses, treatment feedback, practice profiles, and freehand prescriptions
  ([#16](https://github.com/mks-zakaria/sehaty-db/pull/16),
  [`9f51a0b`](https://github.com/mks-zakaria/sehaty-db/commit/9f51a0ba665283010bcef8bc4aa1a95ed3b042f9))


## v1.5.0 (2026-07-14)

### Features

- Add clinic patient register (ClinicPatient) linked to appointments
  ([#14](https://github.com/mks-zakaria/sehaty-db/pull/14),
  [`b57f3c1`](https://github.com/mks-zakaria/sehaty-db/commit/b57f3c1c78b41098e526908826f4e9474af3f2c6))


## v1.4.0 (2026-07-14)

### Features

- Add persistent languages column to doctor_profiles
  ([#12](https://github.com/mks-zakaria/sehaty-db/pull/12),
  [`c0f9297`](https://github.com/mks-zakaria/sehaty-db/commit/c0f929784cde3f146ca3ef83bd2713153ffcdd22))


## v1.3.0 (2026-07-14)

### Code Style

- Ruff format auth models ([#10](https://github.com/mks-zakaria/sehaty-db/pull/10),
  [`b83c71a`](https://github.com/mks-zakaria/sehaty-db/commit/b83c71a59f0c82893d59aeb971a33c1eb7833587))

### Features

- Add auth support tables ([#10](https://github.com/mks-zakaria/sehaty-db/pull/10),
  [`b83c71a`](https://github.com/mks-zakaria/sehaty-db/commit/b83c71a59f0c82893d59aeb971a33c1eb7833587))

- Add auth support tables (refresh tokens, phone OTP)
  ([#10](https://github.com/mks-zakaria/sehaty-db/pull/10),
  [`b83c71a`](https://github.com/mks-zakaria/sehaty-db/commit/b83c71a59f0c82893d59aeb971a33c1eb7833587))


## v1.2.0 (2026-07-14)

### Features

- Add performance indexes (GIST geopoint + btree joins)
  ([#8](https://github.com/mks-zakaria/sehaty-db/pull/8),
  [`2011ea9`](https://github.com/mks-zakaria/sehaty-db/commit/2011ea93847dbea4ca4493a140a81794cee6cc0d))


## v1.1.0 (2026-07-14)

### Features

- Add baseline schema migration (PostGIS geo, enums, all domains)
  ([#6](https://github.com/mks-zakaria/sehaty-db/pull/6),
  [`777209e`](https://github.com/mks-zakaria/sehaty-db/commit/777209eb4d732eed1a0bc46b4076c14a6107e85f))


## v1.0.0 (2026-07-14)

- Initial Release
