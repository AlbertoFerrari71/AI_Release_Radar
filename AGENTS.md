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
- [F] Di default Codex non puo' fare merge su `main`; dal 0065 l'unica eccezione e' la `ASF Auto-Merge Policy` per step L0/L1 autorizzati esplicitamente dal prompt e con tutti i gate PASS. Fonte: istruzioni operative `0020-A) AI Release Radar - ASF Pilot Protocol` e prompt `0065-A) AI Release Radar - ASF Auto-Merge Policy Clarification` fornito da Alberto il 2026-06-09.
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

## ASF Auto-Merge Policy

Fonte di questa sezione: prompt `0065-A) AI Release Radar - ASF Auto-Merge Policy Clarification` fornito da Alberto il 2026-06-09.

- [F] Codex puo' eseguire auto-merge solo se tutte le condizioni seguenti sono vere:
  1. lo step e' classificato L0 o L1;
  2. il prompt dello step autorizza esplicitamente auto-review e auto-merge;
  3. tutti i test richiesti sono PASS;
  4. `git diff --check` e' PASS;
  5. `git diff --cached --check` e' PASS;
  6. non sono presenti file `LAST-*` o `latest-*`;
  7. non sono presenti segreti o API key;
  8. non viene introdotto fetch live o accesso rete;
  9. non vengono aggiunte dipendenze esterne;
  10. non vengono modificati file high-risk;
  11. non sono presenti warning non classificati;
  12. la PR e' stata creata correttamente;
  13. il working tree finale e' pulito.
- [F] L0 significa documentation only. Esempi: docs, changelog, decision record. Auto-merge consentito solo se il prompt lo autorizza e i gate sono PASS.
- [F] L1 significa offline deterministic code. Esempi: parser fixture, scoring deterministico, report offline, test offline. Auto-merge consentito solo se il prompt lo autorizza e i gate sono PASS.
- [F] L2 significa network/read-only integrations. Esempi: fetch live, source registry reale, GitHub API, OpenAI docs live. Auto-merge non consentito; PR draft e review manuale.
- [F] L3 significa scheduler/auth/system changes. Esempi: Windows Task Scheduler, token, GitHub settings, hook, permessi, secrets. Auto-merge vietato; consenso esplicito Alberto.
- [F] L4 significa sensitive data / production / external repos. Esempi: dati familiari, gestionali, eSolver, Mansionario, Family Photo Organizer, repo terzi. Auto-merge vietato salvo nuova policy dedicata.
- [F] I file high-risk includono:
  - `AGENTS.md`;
  - `.githooks/*`;
  - `.github/*`;
  - `scripts/*`;
  - `pyproject.toml`, se aggiunge dipendenze o toolchain;
  - file scheduler/task;
  - file contenenti credenziali o config sensibili;
  - qualunque file fuori repo.
- [F] Se uno step modifica `AGENTS.md` o policy operative, auto-merge e' sempre vietato.
- [F] Lo step 0060 ha confermato che, senza questa policy esplicita, il divieto generale di merge su `main` prevale sul prompt dello step.
- [F] Dal 0065 in poi, il prompt puo' autorizzare auto-merge solo nei casi L0/L1 e solo rispettando tutti i gate.
