# Free Riders Recompiled 繁體中文化 MOD

[Free Riders Recompiled](https://github.com/YuutaTsubasa/Free-Riders-Recompiled)（《Sonic Free Riders》的 PC／Linux／Android 重製移植）用的繁體中文化 MOD。

- **文字**：選單、說明、World Grand Prix 劇情字幕、任務說明、暫停選單、結果與系統訊息、教學，共 3,028 句。
- **圖片**：標題 LOGO 下的「索尼克 自由滑板競速」、16 張賽道名稱條、教學標題。
- **用語**：角色名與用語依 SEGA 官方繁體中文（《索尼克賽車 交叉世界》）；見 [glossary.md](glossary.md)。

比賽 HUD（GOAL、LAP、START 等）在原版日文版就是英文，維持原樣。

## 安裝

1. 從 [Releases](../../releases) 下載 zip，解壓。
2. 把 `zh_tw` 資料夾放進 Free Riders Recompiled 啟動器旁邊的 `mods` 資料夾（`mods\zh_tw\mod.ini`）。
3. 在啟動器的 **Mods** 分頁勾選「繁體中文化」。
4. 把**遊戲語言設為日本語**：這個 MOD 取代的是日文的文字檔，所以語音會是日文。

`game.log` 出現 `MODS mod=zh_tw files=8` 就表示有套用。

## 這個 repo 有什麼

只有譯文與工具，**不含遊戲的任何資料或原文**。建置時從你自己的遊戲檔產生。

| 路徑 | 內容 |
| --- | --- |
| `zh/batch*.json` | 譯文，以翻譯單位編號（`u0001`…）為鍵 |
| `glossary.md` | 用語表與口吻規則 |
| `tools/prepare.py` | 從你的遊戲檔匯出原文，產生 `source/` 與 `units/`（翻譯單位與其日文、英文） |
| `tools/check.py` | 檢查譯文：行數、每行寬度、殘留假名、控制碼 |
| `tools/build.py` | 建置 MOD 到 `build/zh_tw` |
| `tools/banners.py`、`logo.py`、`labels.py` | 重畫有日文字的貼圖 |

## 自己建置

需要 Free Riders Recompiled 的原始碼（`scripts/sfr_font_text.py`、`scripts/sfr_texture.py`、`scripts/unpack_assets.py`，以及執行檔的 `SFR_DUMP_DECOMPRESSED`；格式說明在該 repo 的 `docs/translation.md`），Python 3 與 Pillow、NumPy、fontTools，以及 Noto Sans TC（`NotoSansTC-VF.ttf`）。

1. **取得解壓後的語言檔**：分別用日文與英文各玩一次（進到主選單、World Grand Prix 劇情、教學），執行時設定
   `SFR_DUMP_DECOMPRESSED=<資料夾>`，再用
   `python scripts/unpack_assets.py <資料夾> <遊戲資料夾> <輸出資料夾>` 拼回檔案。
   需要的檔案：`advJ gxfJ gxfrJ pauseFJ resiFJ FNT_SJ s08tfJ s08tsuiJ` 與對應的 `…E`。
2. 把日文檔放進 `originals/`，然後：
   ```bash
   python tools/prepare.py originals <英文檔資料夾> <Free Riders Recompiled 原始碼>
   python tools/check.py zh/*.json
   python tools/build.py originals <Free Riders Recompiled 原始碼> [輸出資料夾] [--title "索尼克 ○○"]
   ```

`originals/`、`source/`、`units/` 與 `build/` 都由你的遊戲檔產生，不要提交。

## 授權

工具與譯文以 [MIT](LICENSE) 授權。《Sonic Free Riders》及其文字、圖片的權利屬於 SEGA；本 MOD 為非官方的粉絲作品。
