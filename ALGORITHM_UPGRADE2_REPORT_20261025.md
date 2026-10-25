# 第二轮算法升级报告（2026-10-25 → 10-26）

## 结论（数字先行）

| 项目 | 结果 | 对照 |
|---|---|---|
| 归档整体压缩（新写入器 V，τ_H = 1e-6） | **1,401 倍**（95% CI 1,245–1,594），8.50 TB → 约 6.1 GB | revision 11 的 W 555 倍（15.3 GB）；V/W = **2.52**（2.38–2.68） |
| 归档整体压缩（V，τ_H = 1e-4） | **4,719 倍**（3,585–6,052），约 1.8 GB | W（修正后）1,735 倍；V/W = **2.72**（2.22–3.31） |
| 结构因子预测（SFP），92 个材料，1e-6 | W2S/W1S 中位数 **1.95**（1.79–2.07），89/92 更小 | 最强基线 O2S（同残差上的运算最优分配）/W2S = 0.995：闭式解仍在最优处 |
| 磁化流 W2M vs 逐点编解码器 | 中位数 **30.1 倍**更小（298/300），1e-4 时 31.1 倍（291/293） | 逐点最优（ZFP/SZ3/SPERR）同一分区、同一 Henkelman 二进制核验 |
| 分区修正（T/O/W/Q） | 1e-6 几乎不变（≤0.07%）；1e-4 下降 2.4–4.8% | 见第 3 节 |

全部判据：研究 3 的 G1、G2、有效性 **均满足**；研究 4 的 A1、M1、有效性 **均满足**。

## 1. 三个方向及选择理由（计划 `D:\Research\QoI-algo2-20261025\paper\nc_reopen\ALGORITHM_UPGRADE2_PLAN_20261025.md`）

- **D5 结构因子预测（SFP，密度写入器）**：revision 11 归档中，只有 1 个或 2 个对称操作的晶胞占了约 75% 的密度字节，对称预测在这些晶胞上无能为力；用存储结构的结构因子 × 每壳层每元素的二次形状因子来预测傅里叶系数，再用水填充写入器编码残差。
- **D4 W2M（磁化写入器）**：1e-4 时磁化流占 revision 11 归档字节的 64–65%，且仍由逐点编解码器写入；每原子磁矩是 Bader 盆地上的线性积分算子，其谱随 q 衰减（Porod 定律 q^-4，与 Hartree 权重同阶），因此用 Hartree 律的步长、以磁矩证书确定步长尺度。
- **分区修正（正确性）**：`certify_m` 用同一个 id 缓存解码分区，导致 revision 10（T、O）与 revision 11（W、Q）中第一个 (writer, τ) 之后的磁矩证书都用了第一个写入器 1e-6 解码密度的分区；重跑时每个解码密度都重建自己的分区。

## 2. 各方向关键数字

### 研究 3：SFP，92 个法则协议材料（60 P1 体相 + 32 P3b 表面），`D:\Research\QoI-algo2-20261025\analysis\sfp_spin_writer_20261025\results\RESULTS.md`

| 比值（认证压缩比之比，中位数，95% CI，胜/总） | τ = 1e-6 | τ = 1e-4 |
|---|---|---|
| W2S/W1S（预测带来的增益） | 1.95（1.79–2.07），89/92 | 1.28（1.12–1.34），68/92 |
| O2S/W2S（最强基线：运算最优 / 闭式） | 0.995（0.993–0.998） | 0.947（0.926–0.962） |
| W2S/A3（revision 10 运算最优，zlib 容器） | 4.47，92/92 | 3.36，92/92 |
| W2S/A6（逐点编解码器） | 69.4，92/92 | 67.2，92/92 |
| W2/W1S（只有预测 vs 只有对称） | 1.00（46/92） | 0.89（41/92） |

- 按对称操作数（1e-6）：1 个操作 2.40（18 个材料），2–8 个 2.09，9–24 个 1.34，>24 个 1.06。
- 按队列：P1 2.05 / P3b 1.79（1e-6）。
- W1S 与 revision 11 字节完全一致：92/92（两个容差）。全部 736 行证书 Hartree RMS < τ。

### 研究 4：300 个归档对象，`D:\Research\QoI-algo2-20261025\analysis\archive_w2_20261025\results\RESULTS.md`

| 写入器 | 1e-6 | 1e-4 | 磁化字节占比 1e-6 / 1e-4 |
|---|---|---|---|
| V（SFP 密度 + W2M 磁化） | **1,401（1,245–1,594）** | **4,719（3,585–6,052）** | 3.8% / 34.1% |
| VP（SFP 密度 + 逐点磁化） | 966 | 1,967 | 33.6% / 72.5% |
| W（revision 11，修正后） | 555（492–635） | 1,735（1,470–2,048） | 19.4% / 65.2% |
| O（revision 10 运算最优，修正后） | 347（317–387） | 1,325（1,158–1,511） | 12.0% / 49.4% |
| L（闭式律） | 316 | 1,036 | – |
| T（截断，修正后） | 232 | 1,115 | – |
| P（逐点最优） | 34.6 | – | – |

- **归因（定义该结论的数字）**：V/W = 密度 (VP/W) × 磁化 (V/VP)：1e-6 时 1.74 × 1.45 = 2.52；1e-4 时 1.13 × 2.40 = 2.72。1e-6 主要来自密度预测，1e-4 主要来自磁化写入器。
- 与最强归档基线比：V/O 4.03（1e-6）、3.56（1e-4）；V/W 2.52、2.72。
- 磁化流（M1）：全体中位 63 字节 vs 逐点 3,189 字节；磁性对象（128 个）11.1 倍（532 vs 6,103 字节，126/128）；零场对象（172 个）51.6 倍。逐点更小的仅 2 个对象（mp-1818959、mp-3150861）。
- Porod 指数（解码 Bader 分区指示函数谱，壳 2–24）：中位 **−2.96**（IQR −3.23 至 −2.72，n = 299），Porod 律理论值 −4。
- 证书：V、T、O、W、Q 在两个容差下 300/300 密度证书，Hartree 违规 0；V/VP 全部磁矩证书经 Henkelman 二进制确认，最大误差 0.00995 / 0.00998 μB（< 0.01）。1e-4 下 7 个对象的解码分区无法通过磁矩合同，按协议存储参考原子图。

## 3. 分区修正：旧值 → 新值（整体压缩倍数），`D:\Research\QoI-algo2-20261025\analysis\archive_partition_fix_20261025\results\RESULTS.md`

| 写入器 | τ = 1e-6 | τ = 1e-4 |
|---|---|---|
| T（截断） | 232.5 → 232.5（0.00%） | 1,142 → **1,115**（−2.36%） |
| O（运算最优） | 347.2 → 347.3（+0.04%） | 1,371 → **1,325**（−3.37%） |
| W（水填充写入器） | 555.2 → 555.2（0.00%） | 1,818 → **1,735**（−4.54%） |
| Q（同写入器运算最优） | 558.4 → 557.9（−0.07%） | 1,813 → **1,726**（−4.81%） |

1e-4 时 4（T）、8（O）、8（W）、6（Q）个对象改用参考原子图；W 的磁化占比 63.5% → 65.2%，W/O 1.33 → 1.31，L/T 0.907 → 0.929。密度流、Hartree 证书、L、P 不受影响。

## 4. 审核

- 两个聚合器从 `analysis\server_runs_20261025c\collected\checkpoints\{sfp,v,trunc,w1}` 重跑：SUMMARY.json、rows.csv、materials.csv、objects.csv 与监控写入的逐字节一致。
- 独立复算：`D:\Research\QoI-algo2-20261025\analysis\sfp_spin_writer_20261025\review_recompute.py`、`D:\Research\QoI-algo2-20261025\analysis\archive_w2_20261025\review_recompute.py`（输出 `results\REVIEW_RECOMPUTE.json`），所有中位数、胜数、N、点估计和配对比值与 SUMMARY.json 一致（相对误差 < 1e-12）。
- tarball SHA-256 复核：ed7e01c1d1173e416e9579046d80c40c9526ac4f4850f860c0e2fa5ad2efca4f（与 SHA256SUMS 一致）。
- 结果提交：`research/algo-upgrade2-20261025` 上 `c68c605`（已推送）。

## 5. 进入 revision 12 的内容

- 分支 `paper/nc-rev12-20261025`，工作树 `D:\Research\QoI-nc-rev12-20261025`；文本提交 `bcf2a0a`，构建提交 `8db826d`（均已推送）。
- PDF：`D:\Research\QoI-nc-rev12-20261025\figures\nc\release\NC_manuscript_20261026_rev12.pdf`（18 页）
- DOCX：`D:\Research\QoI-nc-rev12-20261025\figures\nc\release\NC_manuscript_20261026_rev12.docx`
- 摘要与 Discussion：555 倍 → **1,401 倍**；Results 新增 SFP 段落（1.95 倍、按对称类、O2S 0.995/0.947、对 A3 4.47 倍）；归档段落改为 V（6.1 GB、1,401 倍、对 W 2.52 倍、归因 1.74/1.45；1e-4 4,719 倍、磁化写入器 2.40 倍、63 vs 3,174 字节、磁化占比 65% → 34%），并写明磁矩算子与实测 Porod 指数 −2.96；所有 T/O/W/Q 数字改为修正值。
- Methods：“Water-filling and predictive writers” 增一段（SFP 拟合、门限、W2M 搜索与二进制核验）；Table 1 增两行（`4102390`、`c68c605`）。
- SI：新增 Supplementary Note 4（4.1 预测写入器、4.2 92 材料表、4.3 磁化写入器与 Porod 指数、4.4 归档表与归因）；原 Note 4–10 顺延为 5–11；Note 3.4、5.4 用修正值。
- `DECISIONS.md` 新增 “Revision 12 (2026-10-26)” 节（含修正的原因与新旧值）；`SOURCE_FILES.md` 指向新结果文件。
- 检查：正文 + Methods **4,998** 词，摘要 **150** 词；`audit_manuscript.py --final` 0 失败 0 警告；`test_scientific_claims.py` 21 项全部通过（新增 `test_predictive_writer`、`test_predictive_archive`，改写两个归档测试）；`numcheck.py` 320 个数字全部找到；渲染页 1、8、9、13、16 目检。

## 6. 监控与 Vanda

- 监控任务 `qoi-algo2-monitor-60m`，监控总台 id `qoi-algo2-20261025`，监控目录 `D:\Research\QoI-ext-cache\monitor-algo2-20261025`。
- Vanda 作业（`D:\Research\QoI-ext-cache\monitor-algo2-20261025\jobs.json`）：probe 1492816；研究 3 production 1492899；研究 4 production 1492900（small）/ 1492901（large）；研究 5 production 1492902（small）/ 1492903（large）。
- 清理：`/scratch/junbotong/qoi-algo2-20261025`（11 GB）已删除，`ls` 确认不存在。清理后 `/scratch/junbotong` 列表：Dynamic_SMSI_D3_sensitivity_20261013、Dynamic_SMSI_stage3_units_CH4_20260924、Dynamic_SMSI_stage4_Ce4Ox_layers_20260928、Dynamic_SMSI_stage5_cluster_layer_20260930、Dynamic_SMSI_stage7_first_CH_cleavage_20261015、home_offload、offload_20260923.log、qoi-jhtdb-20261001、qoi-jhtdb-smoke、qoi-srv-20261024、qoi-wpi-20261001、qoi-wpi-20261001-stale-120533、qoi-xcl-20261025、Rh-CeO2-reproduction、wt48_watchdog。其他目录与作业（1480807、1480808 正在运行）未触碰。
