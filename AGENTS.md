# Pixel Composer 汉化工程 - OpenCode 工作指南

## 交互要求

- Thinking思考过程用中文表述
- Reply回答也要用中文回复

---

## 一、项目结构

```
Pixel-Composer-Chinese-Localization/
├── en/                        # 英文源文件（gitignore忽略，不纳入版本控制）
│   ├── config.json
│   ├── fonts/
│   ├── junctions.json
│   ├── nodes.json
│   ├── notes/
│   └── words.json
├── zh/                        # 中文翻译文件（主要工作目录）
│   ├── config.json            # 翻译配置
│   ├── fonts/fonts.json       # 字体配置
│   ├── junctions.json         # 节点参数引用说明
│   ├── nodes.json             # 节点定义翻译（嵌套结构）
│   ├── notes/                 # 参考文档翻译
│   └── words.json             # 界面词库翻译（扁平键值对）
├── Nodes/                     # 本地节点文件翻译（Actions等）
├── Welcome files/             # 汉化教程文件
├── 辅助工具/                   # 辅助脚本工具
├── 一键汉化工具/               # 一键安装器
└── 历史版本存档/               # 旧版汉化归档
```

### 需要翻译的文件类型

#### 1. 界面词库文件 (words.json)

**格式**：扁平键值对 `{"key": "中文翻译"}`

**作用**：菜单、按钮、对话框、节点分类名等UI文本

**特点**：无嵌套结构，key为英文snake_case

示例：
```json
{
  "save": "保存",
  "cancel": "取消",
  "add_node": "添加节点"
}
```

#### 2. 节点定义文件 (nodes.json)

**格式**：嵌套JSON，每个节点包含：
- `name`: 节点显示名称
- `tooltip`: 节点功能说明（可选）
- `inputs`: 输入参数数组
- `outputs`: 输出参数数组（可选）

**参数对象结构**：
- `name`: 参数名（必须翻译）
- `tooltip`: 参数提示（可选，有则翻译）
- `display_data`: 下拉选项数组（可选，含 `-1.0` 分隔符，有则翻译）

示例：
```json
"Node_2D_Light": {
  "name": "2D光源",
  "tooltip": "在图像上应用不同形状的光源。",
  "inputs": [
    { "name": "输入面" },
    { "name": "光源形状", "display_data": ["点光源", "椭圆光", -1.0, "线光源"] },
    { "name": "衰减方式", "tooltip": "控制光源随距离衰减的方式。" }
  ],
  "outputs": [
    { "name": "输出面" }
  ]
}
```

#### 3. 连接点引用文件 (junctions.json)

**格式**：`节点ID -> 参数名 -> 引用备注` 的嵌套映射

**作用**：标记特定节点参数需要的额外参考文档

#### 4. 本地节点文件 (Nodes/ 目录)

**格式**：单个JSON文件，对应 `%LOCALAPPDATA%/PixelComposer/Nodes` 下的节点

目前主要翻译 `Actions/` 下的节点。

---

## 二、汉化核心原则

### 界面词库翻译策略

#### 中文编程函数命名法（"到"字结构）

**类型转换统一用"到"字结构**：
- 无前置类型 = Variant（变体/通用型），直接"到结果"
- 有前置类型 = 专用型，"类型到结果"

排序逻辑：
- `到文本`、`到数值` ← 通用，排最前
- `颜色到文本`、`二维到文本` ← 专用，排后面

**设计优势**：搜索"到"先看到通用函数；搜索"颜色"能命中专用函数。

#### 动宾结构

动作类词汇用动词+名词的动宾结构，省略冗余介词：
- `Load File` → `加载文件`（非"加载一个文件"）
- `Save Project` → `保存项目`

#### 状态/属性类

名词/形容词类词汇直接标签化：
- `Active` → `启用`
- `Visible` → `可见`

### 术语一致性映射表（必须遵守）

| 英文 | 中文 | 说明 |
|------|------|------|
| Surface | 面 | 输入用"输入面"，输出用"输出面" |
| Array | 数组 | 数据集合 |
| Map | 贴图/映射 | 纹理输入叫"XX贴图"，函数映射叫"XX映射"（如"强度贴图"/"强度映射"） |
| Mask | 遮罩 | 透明度/选区遮罩 |
| Blend | 混合 | 混合模式 |
| Dimension | 维度/尺寸 | 画布大小用"尺寸"，抽象空间用"维度" |
| Sprite | 精灵 | 游戏术语保留 |
| Texture | 纹理 | 3D/贴图语境 |
| Atlas | 图集 | 精灵图集 |
| Frame | 帧 | 动画帧 |
| Keyframe | 关键帧 | 动画术语 |
| Path | 路径 | 矢量路径 |
| Node | 节点 | 图节点 |
| Graph | 图 | 节点图表，分类名用"图"，面板名用"图表" |
| Inspector | 检视器 | 属性面板 |
| Preview | 预览 | 实时预览 |
| Export | 导出 | 文件输出 |
| Import | 导入 | 文件输入 |
| Render | 渲染 | 生成图像；相机输出叫"渲染结果"，通用输出叫"输出图像" |
| Shader | 着色器 | GPU程序 |
| SDF | SDF | 保留英文缩写，不翻译 |
| VFX | 特效 | Visual Effects |
| Rigid | 刚体 | 物理刚体 |
| Particle | 粒子 | 粒子系统 |
| Spawn | 生成 | 创建实例 |
| Loop | 循环 | 重复执行 |
| Seed | 种子 | 随机种子 |
| Wiggle | 抖动 | 随机扰动 |
| Over | 随时间变化/生命周期 | 参数名前缀用"随时间变化/随生命周期变化"（如"随生命周期变化的颜色"）；Override节点名叫"覆盖" |
| By | 按/随 | "Rotate by Direction" = "按方向旋转"，"Rotate by Speed" = "按速度旋转" |
| Amount | 数量 | 计数 |
| Strength | 强度 | 效果强度 |
| Range | 范围 | 数值范围 |
| Offset | 偏移 | 位置偏移 |
| Scale | 缩放 | 尺寸变化 |
| Position | 位置 | 坐标 |
| Rotation | 旋转 | 角度 |
| Anchor | 锚点 | 变换中心 |
| Origin | 原点 | 坐标原点 |
| Threshold | 阈值 | 临界值 |
| Feather | 羽化 | 边缘柔化 |
| Invert | 反转 | 黑白翻转 |
| Clamp | 钳制 | 限制范围 |
| Repeat | 重复 | 平铺重复 |
| Empty | 空白 | 过采样选项"空白"（非"空"） |
| Active | 启用 | 开关状态 |
| Mode | 模式 | 工作模式 |
| Type | 类型 | 分类 |
| Style | 样式 | 外观 |
| Shape | 形状 | 几何形状 |
| Object | 物体/对象 | 通用叫"物体"，技术复合词叫"XX对象"（如"网格体对象"、"曲线对象"） |
| Mesh | 网格体 | 3D网格 |
| Collection | 资料夹 | 项目资源管理 |
| Tunnel | 通道/隧道 | 分类名用"通道"，节点名用"隧道发送器/隧道接收器" |
| Filter | 效果 | 图像效果节点分类 |
| Strand | 毛发 | 毛发模拟 |
| Fluid | 流体 | 流体模拟 |
| Preset | 预设 | 预设配置 |
| Palette | 调色板 | 颜色调色板 |
| Gradient | 颜色渐变 | 渐变编辑器 |
| Grid | 网格 | 视图网格 |
| Canvas | 画布 | 绘制画布 |
| Widget | 小工具 | 界面控件 |
| Workshop | 创意工坊 | Steam创意工坊 |
| Metadata | 元数据 | 项目元信息 |
| Wireframe | 线框 | 3D线框渲染 |
| Backface Culling | 背面剔除 | 3D渲染优化 |
| Ambient Occlusion | 环境光遮蔽 | AO |
| Normal | 法线 | 3D法线 |
| Depth | 深度 | 3D深度 |
| Displace | 置换 | 3D置换/变形 |

---

## 三、节点文件汉化规范

### 节点名称翻译

**格式**：`Node_英文域名_功能名` → `中文功能名`

**命名规则**：
1. 保留技术前缀（MK/VFX/3D/2D等）作为标识
2. 核心功能意译
3. 避免过度翻译软件特有名词

示例：
```json
"Node_Blur_Bokeh": "散景模糊",
"Node_3D_Camera": "3D摄像机",
"Node_MK_Fall": "MK落叶",
"Node_VFX_Spawner": "VFX生成器",
"Node_Tunnel_In": "隧道发送器",
"Node_Tunnel_Out": "隧道接收器",
"Node_3D_Displace": "3D置换"
```

### 参数名翻译

**核心原则**：参数名 = 属性标签，不是句子

| 英文参数 | 中文 | 规则 |
|---------|------|------|
| Surface In | 输入面 | 输入统一叫"输入面" |
| Surface Out | 输出面 | 输出统一叫"输出面" |
| Strength Map | 强度贴图 | 带Map=贴图（输入） |
| Mask Feather | 遮罩羽化 | 子属性用"主属性+子功能" |
| Color Over Lifetime | 随生命周期变化的颜色 | Over前面有属性名=随生命周期变化 |
| Speed Over Lifespan | 生命周期速度 | 无前置属性=直接"生命周期+名词" |
| Scale Over Time | 随时间缩放 | Over前面只有Time=随时间变化 |
| Opacity Over Time | 随时间变化的透明度 | 同上 |
| Rotate by Direction | 按方向旋转 | by=按/随，"Rotate by Speed" = "按速度旋转" |
| Spawn Delay | 生成延迟 | 动词+名词=动作+对象 |
| Use Physics | 使用物理 | Use=使用/启用 |
| FOV | 视场角 | 专业缩写保留 |
| Orthographic | 正交 | 技术术语意译 |

### 下拉选项(display_data)翻译

**原则**：选项是用户选择值，必须简短明确。保留 `-1.0` 分隔符不变。

```json
// 混合模式
["正常", "替换", -1.0, "正片叠底", "颜色加深", "线性加深", "最小", -1.0, "相加", "滤色"]

// 动画结束行为
["循环", "往返", "销毁"]

// 分布类型
["均匀", "随机", "泊松"]

// 过采样模式
["空白", "钳制", "重复"]

// 光源形状
["点光源", "椭圆光", "线光源", "非对称线光", "光剑", "聚光灯", "火焰光"]
```

### Tooltip翻译

**原则**：解释功能，不是字面翻译。Tooltip有则翻译，无则保留不添加。

```json
// 正确（功能解释）
"Frames delay between each particle spawn."
→ "每次生成粒子之间的帧延迟。"

// 正确
"Make the particle rotates to follow its movement."
→ "使粒子旋转跟随其运动方向。"
```

---

## 四、汉化工作流程

### 步骤1：读取项目文件

1. 以 `zh/` 目录为主要工作目录
2. 识别目标文件：`words.json` / `nodes.json` / `junctions.json` / `Nodes/` 下文件
3. 如需参考英文原文，可读取 `en/` 下的对应文件（en目录gitignore忽略）

### 步骤2：建立上下文

1. 读取 `zh/` 下已有翻译文件作为参考
2. 对照 `en/` 下的英文原文确认术语
3. 识别未翻译项或需要润色的翻译

### 步骤3：执行翻译

**words.json**：
- 先识别类型转换类（含 to/convert 语义）→ 用"到"字结构
- 再识别动作类（动词开头）→ 动宾结构
- 最后识别状态/属性类（名词/形容词）→ 简洁标签化

**nodes.json**：
- 节点名：前缀保留 + 功能意译
- 参数名：参考术语映射表，确保跨节点一致
- 选项值：参考现有翻译保持一致
- tooltip：有则翻译，无则保留不添加

### 步骤4：一致性检查

1. 同一英文术语全文统一（如 "Surface In" 在所有节点中都译为"输入面"）
2. `-1.0` 分隔符在 display_data 中必须保留
3. JSON格式合法（无尾随逗号）
4. 文件编码为UTF-8

### 步骤5：验证

检查项：
- [ ] 所有翻译项无遗漏
- [ ] display_data 中的 `-1.0` 分隔符已保留
- [ ] 节点名无遗漏
- [ ] 参数名无遗漏
- [ ] tooltip有则翻译，无则保留null/缺失
- [ ] 同一术语全文一致
- [ ] JSON格式合法
- [ ] 文件编码为UTF-8

---

## 五、自建词库维护

翻译过程中如遇到新术语，应在 `zh/` 下维护以下自建词库文件：

### 界面词库 (words_dictionary.json)

按功能分类存储UI词汇翻译：
```json
{
  "general": { "terms": { "save": "保存", "load": "加载" } },
  "view": { "terms": { "zoom_in": "放大", "zoom_out": "缩小" } },
  "nodes": { "terms": { "add_node": "添加节点", "remove_node": "移除节点" } },
  "types": { "terms": { "to_text": "到文本", "to_number": "到数值" } }
}
```

### 节点参数词库 (node_params_dictionary.json)

按节点类型分类存储参数翻译：
```json
{
  "common_params": { "terms": { "Surface In": "输入面", "Mask": "遮罩" } },
  "particle_params": { "terms": { "Spawn Delay": "生成延迟", "Lifespan": "生命周期" } },
  "blur_params": { "terms": { "Strength Map": "强度贴图", "Iteration": "迭代" } }
}
```

### 选项词库 (options_dictionary.json)

```json
{
  "blend_modes": { "terms": ["正常", "正片叠底", "相加", "滤色"] },
  "loop_modes": { "terms": ["循环", "往返", "销毁"] },
  "spawn_types": { "terms": ["持续流", "爆发", "触发"] }
}
```

---

## 六、质量要求

1. **一致性优先**：同一术语全文必须统一，不可出现"输入面"/"表面输入"混用
2. **中文标点**：中文文本用全角标点，英文缩写和文件扩展名保留半角
3. **保留原分隔符**：display_data 中的 `-1.0` 分隔符不可删除或修改
4. **不新增内容**：英文原文没有的 tooltip 不添加，不擅自扩充翻译范围
5. **不做意译过度的润色**：技术术语保持精确，功能说明保持简洁

---

## 七、注意事项

- `en/` 目录已被 `.gitignore` 忽略，仅作本地参考，不纳入版本控制
- 版本号如 `1.20.0.10` 代表基于该版本的Pixel Composer进行的汉化
- `Nodes/` 下的节点文件对应的是 `%LOCALAPPDATA%/PixelComposer/Nodes` 的本地节点
- `junctions.json` 不直接翻译，而是用于标记需要跳转参考文档的参数
- `config.json` 中的 `per_character_line_break: true` 是中文换行配置，不应修改
