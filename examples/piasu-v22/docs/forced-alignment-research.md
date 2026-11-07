# Research 纪要 · 日文歌词逐字时间轴的最优解 · 2026-11-02

**要解决的问题**（一句话，可证伪）：
> 已知歌词全文 + 人声轨，能不能拿到「每个字/每个摩拉在几分几秒」的精确时间戳，且误差 ≤50ms？

**边界**（这次**没有**查什么）：
- 没有实测任何需要装包的方案（torchaudio / qwen-asr 都没装，只核了可装性）
- 没有查商业 API（ElevenLabs / 讯飞等）的价格与条款，因为不想引入按次付费
- 没有查歌声合成反向用的方案（Sinsy / NEUTRINO 的 phoneme 导出），那是另一条路

---

### 结论（每条必带出处；指不出出处就写「未验证」）

| # | 结论 | 数值 | 出处 | 强度 |
|---|---|---|---|---|
| 1 | 阿里开源了**专门做时间戳**的模型 `Qwen3-ForcedAligner-0.6B`，**支持日语**，单次 ≤5 分钟，非自回归（NAR） | 11 语种 / 0.6B 参数 | https://huggingface.co/Qwen/Qwen3-ForcedAligner-0.6B-hf §Overview ／ https://github.com/QwenLM/Qwen3-ASR §Released Models ／ https://qwen.ai/blog?id=qwen3asr §Model List | ✅ 多源交叉 |
| 2 | 官方称其时间戳精度**超过 MFA / CTC / CIF / E2E** 四类对齐器 | 无公开数值 | https://qwen.ai/blog?id=qwen3asr §Qwen3-ForcedAligner | ⚠️ 单源，待二次验证 |
| 3 | 该系列**整套 Apache 2.0**（可商用） | — | https://qwen.ai/blog?id=qwen3asr §Model List | ⚠️ 单源，待二次验证 |
| 4 | PyPI 上 `qwen-asr` 真实存在，最新 0.0.6 | 0.0.6 | https://pypi.org/project/qwen-asr/ ＋ 本地 `pip index versions qwen-asr` | ✅ 多源交叉（官方文档 + 本地实测） |
| 5 | ⚠️ 对齐器的 `Audio Types` 只写了 **Speech**，唱歌是否在范围内**官方没承诺**（ASR 那两个模型才写了 Singing Voice） | — | https://huggingface.co/Qwen/Qwen3-ForcedAligner-0.6B-hf §Available Checkpoints | ⚠️ 单源，待二次验证 |
| 6 | `torchaudio` 自带多语种强制对齐三件套 `MMS_FA`（模型 + tokenizer + aligner），一行 `bundle.get_aligner()` 就能用 | — | https://docs.pytorch.org/audio/2.6.0/tutorials/forced_alignment_for_multilingual_data_tutorial.html §Creating the pipeline | ✅ 多源交叉 |
| 7 | 日语走 MMS_FA **必须先分词 → 罗马化 → 去标点**，它会拿这条归一化链当输入 | — | 同上 §Normalizing the transcript ／ https://github.com/armandli/get-skilled/blob/main/skills/torchaudio-guide-python/references/WAV2VEC2-AND-ASR.md §Multilingual alignment | ✅ 多源交叉 |
| 8 | MMS_FA 实测精度：**中位误差 16–37ms**，词级 250ms 内命中 **96.4%（混音）/ 97.1%（人声轨）** | 96.4% / 97.1% / 16–37ms | https://www.genflick.com/blog/lyric-timestamps-and-forced-alignment-benchmark-2026-10-02 §Accuracy（27 首歌基准） | ⚠️ 单源，待二次验证 |
| 9 | MMS_FA 速度：笔记本 CPU 上**1 分钟歌约 5 秒** | ~5s/min | https://www.genflick.com/blog/lyric-timestamps-and-forced-alignment-benchmark-2026-10-02 §Price and speed | ⚠️ 单源，待二次验证 |
| 10 | ⚠️ MMS 权重是 **CC-BY-NC-4.0**（非商用） | — | https://github.com/0xShug0/audio.cpp/blob/main/docs/models/mms_forced_aligner.md §Limits and license | ⚠️ 单源，待二次验证 |
| 11 | `torchaudio` 自 2.8 起进入维护期，`forced_align` 已弃用、2.9 移除（`Wav2Vec2FABundle` 仍是入口） | 2.8 弃用 / 2.9 移除 | https://docs.pytorch.org/audio/2.9.0/tutorials/forced_alignment_for_multilingual_data_tutorial.html §Warning ／ 同 #7 armandli §Forced alignment | ✅ 多源交叉 |
| 12 | Whisper 的时间戳**系统性偏早**：中位 −127ms，90 分位偏差 **396ms**；中文实测进点早 0.2–1.1s、句尾最多早 1.4s | −127ms / 396ms / 0.2–1.4s | https://www.genflick.com/blog/lyric-timestamps-and-forced-alignment-benchmark-2026-10-02 §Early, late, or just noisy ／ https://vocus.cc/article/6ab41b17fd89780001a019ec §踩坑紀錄 | ✅ 多源交叉（+ 我本地实测「立ち止まってる」早约 1.0s，三方一致） |
| 13 | 对齐器有个通病：**把前奏整段塞给第一个词**（实测 0.6s vs 真实 10.0s）⇒ 必须用**人声分轨**对齐 | 0.6s vs 10–10.5s | 同 #8 §Watch the first word ／ https://octavia.lunartech.ai/blog/forced-alignment-explained §Long silences | ✅ 多源交叉 |
| 14 | 存在**专门为歌词微调**的对齐模型 `Echora MMS-300M`，支持日语（用假名读音），且就是**在人声分轨上训练的** | 7 语种 / 0.3B | https://huggingface.co/hcX02/echora-mms-300m-multilingual-lyrics-forced-aligner §Model Details | ⚠️ 单源，待二次验证 |
| 15 | ⛔ 但 Echora **只授权个人非商用**，禁止商用产品/付费服务/再分发 | — | https://huggingface.co/hcX02/echora-mms-300m-multilingual-lyrics-forced-aligner §Use Restrictions | ⚠️ 单源，待二次验证 |
| 16 | 有现成的日文卡拉 OK 打轴管线可直接抄逻辑：`FA-Kara`、`Forced-Alignment-For-NicoKara`（都是 MMS_FA + janome/pykakasi + 静音切句） | — | https://www.github.com/Xuan-cc/FA-Kara §README ／ https://github.com/oHEILIo/Forced-Alignment-For-NicoKara ／ https://deepwiki.com/moriwx/FA-Kara/1-overview | ✅ 多源交叉 |
| 17 | MFA 有官方日语声学模型 `japanese_mfa` v3.0.0（CC BY 4.0），配 222 万词发音词典 | v3.0.0 / 2,224,242 词 | https://mfa-models.readthedocs.io/en/latest/acoustic/Japanese/Japanese%20MFA%20acoustic%20model%20v3_0_0.html ／ https://huggingface.co/MontrealCorpusTools/japanese_mfa | ✅ 多源交叉 |
| 18 | ⚠️ 但 MFA 日语模型是**朗读语料**训的（Common Voice / JVS），模型卡自己写「as your data diverges from that, you may run into alignment issues」 | — | https://mfa-models.readthedocs.io/en/latest/acoustic/Japanese/Japanese%20MFA%20acoustic%20model%20v3_0_0.html §Performance Factors | ✅ 多源交叉 |
| 19 | **本机现状**：torch 2.14.0+cu126 已装；`torchaudio` **未装**，而 PyPI 上最高只有 **2.11.1**（对不上 2.14） | 2.11.1 vs 2.14.0 | https://pypi.org/project/torchaudio/#history ＋ 本地 `pip index versions torchaudio` | ✅ 多源交叉（本地实证） |

### 本地实测（不是文献结论，单列以免混进「出处」列）

| # | 实测 | 数值 | 怎么测的 |
|---|---|---|---|
| L1 | **本机无 perl** ⇒ MMS_FA 官方推荐的 `uroman` 罗马化脚本跑不了；日语可用 pykakasi 代替且更准 | 无 perl | `perl -v` 无输出 |
| L2 | 本机 faster-whisper **base 模型在 CPU 上转完 123 秒人声轨**，日文歌词基本全对（「ドアのトーコで立ち止まってる 本当は君の方 見てるのに」） | 7.1 秒 / 16 段 | `WhisperModel('base', device='cpu', compute_type='int8')` + `word_timestamps=True` |
| L3 | Whisper 的时间戳在本片实际偏早：它把「立ち止まってる」报在 **13.70**，人声能量段实测是 **14.70** | 早 1.0 秒 | 与 #12 的文献值（0.2–1.4s）同向 |

---

### ⛔ 撤回的旧结论

| 旧结论 | 错在哪 | 现在怎么说 | 影响面 |
|---|---|---|---|
| 「Whisper 时间戳漂 1 秒，这条路不能用」 | 我把「秒数不准」当成「整条路作废」。它**认字是对的**，只是不会看表 | 分工：**Whisper 定归属（哪个字属于哪句、顺序），能量/起音定精确起点** | 只在昨晚的口头结论里，未写入任何派单 |
| 「强制对齐要装 MFA + conda，很重」 | 没查就下了结论。torchaudio 自带 `MMS_FA` 三件套，`bundle.get_aligner()` 一行 | 有一条轻得多的路，代价只是装 torchaudio（本机有版本坑，见 #19） | 未写入派单 |
| 「±0.6s 内找最强起音」是句界判据 | 它会稳定把同一句的中间判成句首（行 2 / 行 3 / 行 15 三次） | 判据换成「有声段数 = 短语数」，或直接上强制对齐 | `分镜表_全曲_v1.md` §1-d 已改；`_v14_lines.py` 的 `SILENCE_PIN` 已改行 3 |

---

### ⛔ 反面样本 / 失败案例（S4）

检索词：`whisper word timestamps inaccurate singing`、`MMS forced aligner failure long silence repeated lines`、`forced alignment limitations`

| 失败模式 | 具体表现 | 出处 |
|---|---|---|
| 前奏被塞给第一个词 | 对齐报 0.6s，真实 10–10.5s | #8 §Watch the first word |
| 长静音会被摊进相邻词 | 「systems that do not handle them well distribute the silence into surrounding words」 | octavia §Long silences |
| 重复句 / 长音 / 拖尾 / 和声 | 「may produce inaccurate boundaries」「identical interjections placed late, first held over the rest」 | Echora 模型卡 §Limitations |
| 稿子和唱的不一致 | 会**照着一个错稿产生一条对齐路径**，且不报错（silently wrong） | octavia §FAQ「Why is my alignment completely wrong in one section」 |
| 罗马字化之后音节边界变弱 | 「Romanized lyrics may have weaker syllable boundaries than native scripts」 | Echora §Limitations |
| 长文件 | 数值稳定性/内存受限，须按自然停顿切块 | octavia §Very long files |

⭐ 这几条正好命中我踩过的坑：行 2 的 `15.800` = 把「たちどまってる」的第 6 个摩拉当成句首，等价于「前奏塞给第一个词」的同一类错误。

---

### 边际收敛记录（S3）

| 轮次 | 检索词 | 新增事实数 |
|---|---|---|
| 1 | forced alignment Japanese lyrics ／ MFA japanese_mfa ／ whisper singing timestamps ／ 歌声 歌詞 アライメント | 8 |
| 2 | torchaudio MMS_FA japanese ／ open source karaoke timing github ／ MMS failure cases ／ Qwen3-ForcedAligner 核实 | 9 |
| 3 | （只做本地可装性核验，不再检索网页） | 4（全部来自本地实测） |

⚠️ 未触顶：第 2 轮仍是 9 条新事实。**但已足够做决策**，剩余待查项已列进「未验证项」。

---

### 联想扩散（D1–D9）

| # | 方向 | 状态 | 检索词 | 找到了什么 |
|---|---|---|---|---|
| D1 | 术语邻居 | ✅ 已查 | forced alignment vs ASR；CIF / E2E / CTC 对齐器 | 对齐 ≠ 识别；四类对齐器实现不同（CTC / GMM-HMM / NAR-LLM / CIF） |
| D2 | 权威源头 | ✅ 已查 | 追到 HF 模型卡 + 官方 blog + MFA 官方模型页 | Qwen 与 MFA 都是一手文档，不是二手总结 |
| D3 | 利益相关 | ✅ 已查 | 各来源是否商业推广 | `genflick` 那篇基准文是**自家产品**的对比博客（ElevenLabs vs MMS），数字有用但立场要打折；Echora 是个人项目 |
| D4 | 前置依赖 | ✅ 已查 | 日语要什么前置 | 分词（janome/sudachi）+ 假名读音（pykakasi）+ 人声分轨（我们已有 Demucs） |
| D5 | 反面/失败 | ✅ 已查 | 见 S4 表 | 6 类失败模式，全部有出处 |
| D6 | 量化参数 | ✅ 已查 | 精度/速度/版本 | 16–37ms 中位；96.4%/97.1%；5s 每分钟；−127ms/396ms（Whisper） |
| D7 | 同类替代 | ✅ 已查 | MFA / MMS_FA / Qwen3-FA / Echora / elevenlabs | 5 条路，按「可商用 / 是否吃唱歌 / 安装成本」三维排 |
| D8 | 跨域差异 | ✅ 已查 | 说话 vs 唱歌；朗读语料训的模型 | MFA 日语模型是朗读语料 ⇒ 唱歌是分布外；Qwen 对齐器只承诺 Speech |
| D9 | 原始材料 | ⚠️ 部分或被动撞见 | 论文 PDF 未下载 | 只读到了模型卡与官方 blog，**没读 Qwen3-ASR 论文原文** |

---

### ⭐ 探索产出（不知道 → 已知）· S6

| # | 我原本以为 | 实际是 | 类别 | 能变成什么动作 |
|---|---|---|---|---|
| 1 | 对齐只能靠 MFA（conda 重装）或商业 API | torchaudio 自带 `MMS_FA` 三件套，`get_aligner()` 一行出词级时间 | 能力 | 有了一条**零付费**的精确对齐路 |
| 2 | 没有专门给「歌词」训的对齐模型 | Echora MMS-300M 就是，且在人声分轨上训的 | 工具 | 但**非商用**，只做技术参考，不能进交付链 |
| 3 | （不知道它存在） | `Qwen3-ForcedAligner-0.6B`，Apache 2.0，支持日语，专做时间戳 | 能力 | ⭐ 首选试跑对象，法律上最干净 |
| 4 | （不知道它存在） | `FA-Kara` / `Forced-Alignment-For-NicoKara` 两个成品打轴管线 | 工具 | 可以直接抄「静音切句 + 尾音修正」的逻辑，省一轮试错 |
| 5 | （不知道它存在） | MFA 有官方日语模型 + 222 万词词典 | 工具 | MFA 这条从「不可行」变成「备选」 |
| 6 | MMS 权重可以随便用 | MMS 是 CC-BY-NC（非商用），Echora 也是 | 选项 | 若片子要卖（Steam），这条排除 |

**U =** 6 ｜ **C =** 2 ｜ **N =** 5（torchaudio 版本坑 / 无 perl / 对齐器只承诺 Speech / MMS 非商用 / Echora 非商用）

⚠️ 判红线：U=6 ≥ 3 ✅ ｜ C=2 ≥ 1 ✅ ｜ N=5 < U=6 ⇒ **非防守型**

---

### 未验证项（明确写"不知道"）

- Qwen3-ForcedAligner **在唱歌上的实际误差**：官方只写了 Speech，没有任何唱歌基准
- Qwen 自评「超过 MFA/CTC」的**具体数字**：blog 只有结论没有表
- MMS_FA 那组 16–37ms 是 **英文歌**基准，日语唱歌没测过
- Echora v8 的日语实际表现：模型卡只给训练方式，没给日语指标
- MFA 用朗读语料模型对唱歌做对齐的实际退化幅度
- 本机 torch 2.14 与 torchaudio 2.11.1 是否真能共存（只核了版本号，没装）

### ⏳ 未决（需要拍板的）

1. **先试哪条**：
   - A. `qwen-asr` + `Qwen3-ForcedAligner-0.6B`（Apache 2.0，~1.2GB，需装 transformers）
   - B. `torchaudio` + `MMS_FA`（免费，但要单独开 venv 装 torch 2.11 一套，~2–3GB）
   - C. 什么都不装，**Whisper 定归属 + 起音定起点**（今天就能出结果）
2. **这片子以后卖不卖**（决定 MMS / Echora 这两条非商用的路能不能进交付链）
3. 三条路**都必须先过副歌这道阳性对照**：能不能复现 60.240 / 105.600 两个已实测锚点，误差 ≤50ms。过不了就不用。

---

## 落地建议（一句话）

**今天就用 C 把 22 行重排**（零安装、已验证可行），**同时花 10 分钟试 A**（法律最干净、专做时间戳）；
A 若过不了副歌对照，就退回 C，不碰 B（版本坑 + 非商用 + 只有英文基准）。
