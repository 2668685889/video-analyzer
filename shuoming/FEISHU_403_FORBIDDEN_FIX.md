# 飞书91403 Forbidden错误解决方案

## 问题描述
在使用飞书多维表格API时遇到`91403 Forbidden`错误，错误信息如下：
```
API请求异常: 403 Client Error: Forbidden for url: https://open.feishu.cn/open-apis/bitable/v1/apps/Z86qbz1etatfhyshNfUc35MTnTb/tables/tbllYJtIsjmyj4ub/records?user_id_type=open_id
API错误详情: {'code': 91403, 'msg': 'Forbidden', 'data': {}}
```

## 错误原因
根据飞书开放平台文档，使用`tenant_access_token`调用多维表格API时，**必须确保应用已经是文档的所有者或协作者**，否则会调用失败。

当前错误的根本原因是：**应用没有被添加为多维表格的协作者**。

## 解决方案

### 方案1：添加应用为多维表格协作者（推荐）

1. **打开多维表格**
   - 访问您的多维表格：`https://eg2uf4p7n7.feishu.cn/base/Z86qbz1etatfhyshNfUc35MTnTb?table=tbllYJtIsjmyj4ub&view=vewcZsiB1e`

2. **添加文档应用**
   - 在多维表格页面右上方点击「...」
   - 选择「...更多」
   - 点击「添加文档应用」
   - 搜索并添加您的应用：`cli_a823d173b53a501c`

3. **设置权限**
   - 为应用分配适当的权限（建议：编辑权限）
   - 确认添加

### 方案2：使用user_access_token（备选）

如果无法添加应用为协作者，可以考虑使用`user_access_token`：

1. **修改鉴权方式**
   - 将`tenant_access_token`改为`user_access_token`
   - 需要实现用户授权流程

2. **权限范围**
   - `user_access_token`的权限范围受限于用户的身份权限
   - 用户必须对目标多维表格有访问权限

## 验证步骤

完成上述配置后，请按以下步骤验证：

1. **重启应用**
   ```bash
   python main.py
   ```

2. **测试连接**
   - 在应用界面点击「测试飞书连接」按钮
   - 确认连接成功

3. **测试同步**
   - 进行视频分析
   - 测试飞书同步功能
   - 检查是否还有403错误

## 权限要求

根据飞书开放平台文档，多维表格API需要以下权限：

- **应用身份权限**：`bitable:app`
- **具体权限**：
  - `bitable:app:readonly` - 读取权限
  - `bitable:app` - 读写权限

## 注意事项

1. **权限申请**：确保在飞书开发者后台已申请相应的API权限
2. **审核流程**：自建应用的权限可能需要企业管理员审核
3. **协作者权限**：添加应用为协作者时，建议分配编辑权限以支持数据写入
4. **token有效期**：`tenant_access_token`有效期为2小时，系统会自动刷新

## 相关文档

- [飞书多维表格API文档](https://open.feishu.cn/document/ukTMukTMukTM/uUDN04SN0QjL1QDN/bitable-overview)
- [API权限申请指南](https://open.feishu.cn/document/ukTMukTMukTM/uQjN3QjL0YzN04CN2cDN)
- [访问凭证选择指南](https://open.feishu.cn/document/ukTMukTMukTM/ukDNz4SO0MjL5QzM)