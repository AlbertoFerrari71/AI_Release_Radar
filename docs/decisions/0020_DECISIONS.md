# 0020) ASF Pilot Protocol Decisions

Fonte principale: istruzioni operative `0020-A) AI Release Radar - ASF Pilot Protocol` fornite da Alberto il 2026-06-09.

## 1. Obiettivo dello step

- [F] Lo step 0020 formalizza la ASF Pilot Mode dentro `AI_Release_Radar`.
- [F] Lo step 0020 collauda il primo flusso ASF reale: branch di step, modifiche, verifiche, commit, push branch, PR draft, stop.
- [F] Lo step 0020 e' documentale, di governance e di pilot protocol.
- [F] Lo step 0020 non implementa codice applicativo del radar.

## 2. Decisione: `AI_Release_Radar` come primo pilota ASF reale

- [F] `AI_Release_Radar` e' il primo progetto pilota reale di AI Software Factory.
- [INT] Il repository viene usato per validare un flusso operativo ripetibile prima degli step applicativi successivi.

## 3. ASF Pilot Mode

- [F] Codex puo' operare su branch di step.
- [F] Codex puo' creare modifiche documentali, verifiche Git, commit, push del branch di step e PR draft.
- [F] Codex deve fermarsi alla PR draft.
- [F] Codex non puo' fare merge su `main`.
- [F] Codex non puo' fare push diretto su `main`.
- [F] Codex non puo' usare `--no-verify`.
- [F] Codex non puo' fare force-push.
- [F] Codex non puo' creare tag o release.
- [F] Codex non puo' attivare scheduler.
- [F] Codex non puo' usare API key di servizi terzi.
- [F] Codex non puo' committare segreti.
- [F] Codex non puo' modificare altri repository.
- [F] Codex non puo' fare deploy.

## 4. GitHub branch protection non disponibile sul piano attuale

- [F] GitHub branch protection server-side non e' disponibile sul repository privato con piano GitHub Free.
- [INT] La protezione server-side viene sostituita temporaneamente da un guardrail locale fino a diversa decisione di Alberto.

## 5. Guardrail locale `.githooks/pre-push`

- [F] Il repository versiona `.githooks/pre-push` come guardrail locale temporaneo.
- [F] Il guardrail blocca push diretti verso `origin main`.
- [F] Il guardrail consente push verso branch di step.
- [F] Alberto ha gia' testato manualmente il guardrail con esito corretto.
- [F] Il guardrail non deve essere bypassato.

## 6. Policy commit/push/PR/merge

- [F] I commit di Codex sono consentiti solo sui branch di step.
- [F] Il push di Codex e' consentito solo sui branch di step.
- [F] Le PR aperte da Codex devono essere draft salvo istruzione esplicita diversa di Alberto.
- [F] Il merge su `main` richiede decisione esplicita di Alberto.
- [F] Il push diretto su `main` e' vietato.
- [F] `--no-verify` e' vietato.
- [F] Force-push, tag, release e deploy sono vietati in questo step.

## 7. Regola no `LAST-*` / no `latest-*`

- [F] I file `LAST-*` sono vietati.
- [F] I file `latest-*` sono vietati.
- [F] Gli output devono usare nomi deterministici numerati o datati.
- [F] In step successivi il progetto potra' usare `runs_index.jsonl` per indicizzare run e output.

## 8. Output Bridge vs repo versionato

- [F] Report di step e output runtime non vanno versionati nel repository.
- [F] Il repository deve contenere solo codice, test, fixture, config e documentazione stabile.
- [F] Eventuali report Bridge devono stare fuori dal repository.
- [F] Il percorso Bridge indicato per questo progetto e' `D:\FG-SAB Dropbox\Alberto Ferrari\ChatGPT_Bridge\AI_Release_Radar\`.

## 9. Gate minimi per ogni step

- [F] Ogni step deve chiudersi con stato.
- [F] Ogni step deve indicare test o verifiche eseguite.
- [F] Ogni step deve indicare il tempo impiegato.
- [F] Ogni step deve indicare il prossimo step consigliato.
- [F] Per lo step 0020 le verifiche obbligatorie includono `git --no-pager status` e `git --no-pager diff --check` prima del commit.
- [F] Per lo step 0020 le verifiche obbligatorie includono il controllo dello stage, `git --no-pager diff --cached --check`, assenza di file vietati nello stage, assenza di output runtime/report nello stage e conferma che `.gitignore` non escluda `.githooks/`.

## 10. Roadmap aggiornata 0030-0150

- [F] 0030) Core Item Model and Snapshot Format
- [F] 0040) Offline Fixture Parser
- [F] 0050) Snapshot and Diff Engine
- [F] 0060) Classification and Relevance Scoring
- [F] 0070) Project Impact Mapping
- [F] 0080) Report Engine
- [F] 0090) CLI Dry Run
- [F] 0100) OpenAI Source Registry and URL Verification
- [F] 0110) First Controlled Live Fetch
- [F] 0120) Noise Reduction and Confidence Calibration
- [F] 0130) Codex Prompt Recommendation Engine
- [F] 0140) Windows Scheduler Framework
- [F] 0150) Codex_Skills Integration / as-common-ai-release-radar

## 11. Prossimo step consigliato

- [F] Il prossimo step consigliato e' `0030) Core Item Model and Snapshot Format`.
