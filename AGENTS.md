# AGENTS.md

## Regole operative

- Non fare commit/push/PR/merge/deploy salvo istruzione esplicita di Alberto.
- Non aggiornare automaticamente Codex, OpenAI tooling, skill, repository o scheduler.
- Distinguere sempre:
  - [F] fatto da fonte;
  - [INT] interpretazione;
  - [IP] ipotesi;
  - [PROP] proposta da approvare.
- Ogni fatto deve avere una fonte.
- Usare output deterministici numerati/datati.
- Non usare file LAST-* o latest-*.

## ASF Pilot Mode

Fonte di questa sezione: istruzioni operative `0020-A) AI Release Radar - ASF Pilot Protocol` fornite da Alberto il 2026-06-09.

- [F] Questo repository e' il primo progetto pilota reale di AI Software Factory.
- [F] Codex puo' fare commit e push solo su branch di step.
- [F] Codex puo' aprire PR draft.
- [F] Codex non puo' fare merge su `main`.
- [F] Codex non puo' fare push diretto su `main`.
- [F] Codex non puo' usare `--no-verify`.
- [F] Codex non puo' fare force-push.
- [F] Codex non puo' creare tag o release.
- [F] Codex non puo' attivare scheduler.
- [F] Codex non puo' usare API key di servizi terzi.
- [F] Codex non puo' committare segreti.
- [F] Codex non puo' modificare altri repository.
- [F] Report di step e output runtime non vanno versionati nel repo.
- [F] Il repo deve contenere solo codice, test, fixture, config e documentazione stabile.
- [F] `LAST-*` e `latest-*` sono vietati.
- [F] Usare file numerati/datati e, piu' avanti, `runs_index.jsonl`.
- [F] Ogni step deve chiudersi con stato, test/verifiche, tempo impiegato e prossimo step consigliato.
- [F] GitHub branch protection server-side non e' disponibile sul repository privato con piano GitHub Free.
- [F] Per ora il progetto usa `.githooks/pre-push` come guardrail locale temporaneo.
- [F] Il guardrail locale `.githooks/pre-push` non deve essere bypassato.
