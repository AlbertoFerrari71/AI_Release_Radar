# 0065) ASF Auto-Merge Policy Clarification

## Context

- [F] Il repository `AI_Release_Radar` e' il primo progetto pilota reale di AI Software Factory in ASF Pilot Mode. Fonte: `AGENTS.md`.
- [F] Gli step 0010, 0020, 0030, 0040, 0050 e 0060 risultano chiusi su `main` prima dello step 0065. Fonte: prompt `0065-A) AI Release Radar - ASF Auto-Merge Policy Clarification`.
- [F] Lo step 0060 ha provato il primo trial di auto-review e auto-merge low-risk. Fonte: prompt `0065-A) AI Release Radar - ASF Auto-Merge Policy Clarification`.
- [F] Nel 0060 i gate tecnici locali erano PASS, ma l'auto-merge e' stato bloccato perche' `AGENTS.md` vietava ancora a Codex di fare merge su `main`. Fonte: prompt `0065-A) AI Release Radar - ASF Auto-Merge Policy Clarification`.
- [F] La PR #5 e' stata poi mergiata manualmente da Alberto. Fonte: prompt `0065-A) AI Release Radar - ASF Auto-Merge Policy Clarification`.

## Decision

- [F] `AGENTS.md` introduce una sezione `ASF Auto-Merge Policy`. Fonte: `AGENTS.md`.
- [F] L'auto-merge Codex e' consentito solo per step L0/L1, solo se il prompt lo autorizza esplicitamente, solo se tutti i gate sono PASS e solo se non vengono toccati file high-risk. Fonte: `AGENTS.md`.
- [F] Se uno step modifica `AGENTS.md` o policy operative, auto-merge e' sempre vietato. Fonte: `AGENTS.md`.
- [INT] Questa decisione chiarisce l'eccezione stretta al divieto generale di merge su `main` senza rendere automatici gli step di governance. Fonte: `AGENTS.md`.

## Risk classes

- [F] L0 e' documentation only. Esempi: docs, changelog, decision record. Fonte: `AGENTS.md`.
- [F] L1 e' offline deterministic code. Esempi: parser fixture, scoring deterministico, report offline, test offline. Fonte: `AGENTS.md`.
- [F] L2 e' network/read-only integrations. Esempi: fetch live, source registry reale, GitHub API, OpenAI docs live. Fonte: `AGENTS.md`.
- [F] L3 e' scheduler/auth/system changes. Esempi: Windows Task Scheduler, token, GitHub settings, hook, permessi, secrets. Fonte: `AGENTS.md`.
- [F] L4 e' sensitive data / production / external repos. Esempi: dati familiari, gestionali, eSolver, Mansionario, Family Photo Organizer, repo terzi. Fonte: `AGENTS.md`.

## Auto-merge allowed cases

- [F] Auto-merge e' consentito per L0 solo se il prompt lo autorizza e i gate sono PASS. Fonte: `AGENTS.md`.
- [F] Auto-merge e' consentito per L1 solo se il prompt lo autorizza e i gate sono PASS. Fonte: `AGENTS.md`.
- [F] Auto-merge richiede PR creata correttamente e working tree finale pulito. Fonte: `AGENTS.md`.

## Auto-merge forbidden cases

- [F] Auto-merge non e' consentito per L2; serve PR draft e review manuale. Fonte: `AGENTS.md`.
- [F] Auto-merge e' vietato per L3; serve consenso esplicito Alberto. Fonte: `AGENTS.md`.
- [F] Auto-merge e' vietato per L4 salvo nuova policy dedicata. Fonte: `AGENTS.md`.
- [F] Auto-merge e' sempre vietato se lo step modifica `AGENTS.md` o policy operative. Fonte: `AGENTS.md`.
- [F] Lo step 0065 modifica `AGENTS.md`, quindi deve fermarsi a PR draft. Fonte: prompt `0065-A) AI Release Radar - ASF Auto-Merge Policy Clarification`.

## High-risk files

- [F] I file high-risk includono `AGENTS.md`, `.githooks/*`, `.github/*`, `scripts/*`, `pyproject.toml` quando aggiunge dipendenze o toolchain, file scheduler/task, file contenenti credenziali o config sensibili e qualunque file fuori repo. Fonte: `AGENTS.md`.
- [INT] La presenza di file high-risk nello scope richiede review manuale perche' puo' cambiare regole operative, sicurezza, automazione o superficie di esecuzione. Fonte: `AGENTS.md`.

## Gate checklist

- [F] L'auto-merge richiede step L0/L1, autorizzazione esplicita nel prompt, test richiesti PASS, `git diff --check` PASS, `git diff --cached --check` PASS, nessun file `LAST-*` o `latest-*`, nessun segreto/API key, nessun fetch live o accesso rete introdotto, nessuna nuova dipendenza esterna, nessun file high-risk modificato, nessun warning non classificato, PR creata correttamente e working tree finale pulito. Fonte: `AGENTS.md`.
- [F] Se una condizione del gate non e' vera, auto-merge non e' consentito. Fonte: `AGENTS.md`.

## Lesson learned from 0060

- [F] Lo step 0060 ha mostrato che il prompt di step non basta a superare una policy repo piu' restrittiva. Fonte: prompt `0065-A) AI Release Radar - ASF Auto-Merge Policy Clarification`.
- [F] Dal 0065 in poi, `AGENTS.md` definisce quando il prompt puo' autorizzare auto-merge e quando resta necessario fermarsi a PR draft. Fonte: `AGENTS.md`.

## What remains manual

- [F] Il merge dello step 0065 resta manuale perche' lo step modifica `AGENTS.md`. Fonte: prompt `0065-A) AI Release Radar - ASF Auto-Merge Policy Clarification`.
- [F] Gli step L2, L3 e L4 restano manuali secondo la classe di rischio. Fonte: `AGENTS.md`.
- [F] Alberto decide il merge su `main` dopo review quando auto-merge non e' consentito. Fonte: prompt `0065-A) AI Release Radar - ASF Auto-Merge Policy Clarification`.

## Next step

- [F] Il prossimo step consigliato e' `0070) Project Impact Mapping`. Fonte: prompt `0065-A) AI Release Radar - ASF Auto-Merge Policy Clarification`.
- [F] Il 0070 potra' essere usato come secondo trial di auto-merge se resta L1 offline deterministic code e se il prompt lo autorizza esplicitamente. Fonte: prompt `0065-A) AI Release Radar - ASF Auto-Merge Policy Clarification`.
