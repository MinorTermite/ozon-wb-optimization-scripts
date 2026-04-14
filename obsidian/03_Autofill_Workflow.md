# Autofill Workflow

Для ready-to-use заметок добавлен локальный генератор.

Скрипт:
- [build_obsidian_ready_prompts.py](C:/Users/GravMix/Desktop/CodexMain/marketplace-missing-card-system/scripts_tool/build_obsidian_ready_prompts.py)

Что делает:
- читает [generated_card_packs.json](C:/Users/GravMix/Desktop/CodexMain/marketplace-missing-card-system/data_dump/generated_card_packs.json);
- выбирает приоритетные браслеты;
- раскладывает готовые заметки в `obsidian/Ready_Prompts/Gemini` и `obsidian/Ready_Prompts/ChatGPT`;
- подставляет получателя, знак зодиака, смысл гравировки, повод и ссылки на эталонные фото.

Запуск:

```powershell
python C:\Users\GravMix\Desktop\CodexMain\marketplace-missing-card-system\scripts_tool\build_obsidian_ready_prompts.py
```

Результат:
- новые готовые заметки появятся в `obsidian/Ready_Prompts/`
- manifest будет лежать в `obsidian/Ready_Prompts/manifest.json`

Что уже умеет хорошо:
- зодиакальные браслеты;
- браслет для мамы;
- браслеты с молитвой и смысловой гравировкой;
- приоритетные gift/prayer/zodiac сценарии.

Где еще нужна ручная голова:
- карточки, где реальная фраза гравировки не вытащилась явно из исходников;
- редкие SKU с неоднозначной семантикой;
- каффы, если по ним нет нормальной структурированной выгрузки.
