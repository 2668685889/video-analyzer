# 快速提示词重复出现问题修复

## 问题描述

用户反映在删除默认的快速提示词后，重新打开软件时，被删除的提示词又重新出现了。

## 问题原因

在原始的数据库初始化代码中，`_insert_default_prompts` 方法使用了 `INSERT OR IGNORE` 语句来插入默认提示词。虽然这可以防止重复插入相同名称的提示词，但存在以下问题：

1. **每次启动都尝试插入**：无论用户是否删除了默认提示词，每次应用启动时都会尝试重新插入
2. **忽略用户意图**：如果用户主动删除了某个默认提示词，系统应该尊重用户的选择，而不是重新添加

## 解决方案

修改 `src/utils/database.py` 文件中的 `_insert_default_prompts` 方法：

### 修改前的逻辑
```python
def _insert_default_prompts(self, cursor) -> None:
    # 直接插入默认提示词，使用 INSERT OR IGNORE
    for prompt in default_prompts:
        cursor.execute("""
            INSERT OR IGNORE INTO quick_prompts (name, prompt_text, description, is_default)
            VALUES (?, ?, ?, ?)
        """, (prompt['name'], prompt['prompt_text'], prompt['description'], prompt['is_default']))
```

### 修改后的逻辑
```python
def _insert_default_prompts(self, cursor) -> None:
    # 检查表中是否已有数据
    cursor.execute("SELECT COUNT(*) FROM quick_prompts")
    count = cursor.fetchone()[0]
    
    # 只有在表为空时才插入默认提示词
    if count == 0:
        for prompt in default_prompts:
            cursor.execute("""
                INSERT INTO quick_prompts (name, prompt_text, description, is_default)
                VALUES (?, ?, ?, ?)
            """, (prompt['name'], prompt['prompt_text'], prompt['description'], prompt['is_default']))
```

## 修复效果

1. **首次使用**：当数据库表为空时（首次使用应用），会自动插入默认的快速提示词
2. **尊重用户选择**：如果用户删除了某些提示词，重新启动应用时不会重新添加这些提示词
3. **保持灵活性**：用户可以完全删除所有提示词，或者只保留自己需要的提示词

## 使用建议

- 如果用户想要恢复默认提示词，可以通过快速提示管理界面手动添加
- 建议用户在删除默认提示词前，先考虑是否真的不需要这些提示词
- 用户可以根据自己的需求创建自定义的快速提示词

## 技术细节

- 修改文件：`src/utils/database.py`
- 修改方法：`_insert_default_prompts`
- 核心改进：添加表数据检查，只在表为空时插入默认数据
- 兼容性：完全向后兼容，不影响现有功能