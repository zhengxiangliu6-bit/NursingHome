<template>
  <div class="alert-rule-config">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>告警规则管理</span>
          <el-button type="primary" @click="handleAdd">新增规则</el-button>
        </div>
      </template>

      <el-table :data="rules" v-loading="loading" stripe>
        <el-table-column label="规则名称" prop="name" min-width="140" />
        <el-table-column label="监测指标" width="110">
          <template #default="{ row }">
            {{ ALERT_METRICS[row.metric]?.label || row.metric }}
          </template>
        </el-table-column>
        <el-table-column label="触发条件" width="160">
          <template #default="{ row }">
            <span class="condition-text">
              {{ ALERT_METRICS[row.metric]?.label || row.metric }}
              {{ ALERT_OPERATORS[row.operator]?.label || row.operator }}
              {{ row.threshold }}
              {{ ALERT_METRICS[row.metric]?.unit || '' }}
            </span>
          </template>
        </el-table-column>
        <el-table-column label="持续时间" width="100">
          <template #default="{ row }">
            {{ row.duration > 0 ? row.duration + '秒' : '立即' }}
          </template>
        </el-table-column>
        <el-table-column label="级别" width="80" align="center">
          <template #default="{ row }">
            <el-tag :type="ALERT_SEVERITY[row.severity]?.type || 'info'" size="small">
              {{ ALERT_SEVERITY[row.severity]?.label || row.severity }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="冷却时间" width="100">
          <template #default="{ row }">
            {{ row.cooldown }}秒
          </template>
        </el-table-column>
        <el-table-column label="启用" width="80" align="center">
          <template #default="{ row }">
            <el-switch v-model="row.enabled" @change="handleToggle(row)" />
          </template>
        </el-table-column>
        <el-table-column label="操作" width="140" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" size="small" link @click="handleEdit(row)">编辑</el-button>
            <el-button type="danger" size="small" link @click="handleDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 新增/编辑弹窗 -->
    <el-dialog v-model="dialogVisible" :title="editingRule ? '编辑规则' : '新增规则'" width="520px">
      <el-form ref="formRef" :model="form" :rules="formRules" label-width="100px">
        <el-form-item label="规则名称" prop="name">
          <el-input v-model="form.name" placeholder="如：心率过高告警" />
        </el-form-item>
        <el-form-item label="监测指标" prop="metric">
          <el-select v-model="form.metric" placeholder="选择指标">
            <el-option v-for="(item, key) in ALERT_METRICS" :key="key" :label="item.label" :value="key" />
          </el-select>
        </el-form-item>
        <el-form-item label="操作符" prop="operator">
          <el-select v-model="form.operator" placeholder="选择操作符">
            <el-option v-for="(item, key) in ALERT_OPERATORS" :key="key" :label="`${item.label} (${item.desc})`" :value="key" />
          </el-select>
        </el-form-item>
        <el-form-item label="阈值" prop="threshold">
          <el-input-number v-model="form.threshold" :precision="1" />
          <span v-if="form.metric" class="unit-label">{{ ALERT_METRICS[form.metric]?.unit }}</span>
        </el-form-item>
        <el-form-item label="持续时间" prop="duration">
          <el-input-number v-model="form.duration" :min="0" :step="10" />
          <span class="unit-label">秒 (0=立即触发)</span>
        </el-form-item>
        <el-form-item label="告警级别" prop="severity">
          <el-radio-group v-model="form.severity">
            <el-radio value="critical">严重</el-radio>
            <el-radio value="warning">警告</el-radio>
            <el-radio value="info">提示</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="冷却时间" prop="cooldown">
          <el-input-number v-model="form.cooldown" :min="0" :step="60" />
          <span class="unit-label">秒 (防重复告警)</span>
        </el-form-item>
        <el-form-item label="启用">
          <el-switch v-model="form.enabled" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { getAlertRules, createAlertRule, updateAlertRule, deleteAlertRule, toggleAlertRule } from '@/api/alertCenter'
import { ALERT_METRICS, ALERT_OPERATORS, ALERT_SEVERITY } from '@/utils/constants'
import { ElMessage, ElMessageBox } from 'element-plus'

const loading = ref(false)
const rules = ref([])
const dialogVisible = ref(false)
const editingRule = ref(null)
const formRef = ref(null)

const defaultForm = {
  name: '',
  metric: '',
  operator: 'gt',
  threshold: 0,
  duration: 0,
  severity: 'warning',
  cooldown: 300,
  enabled: true,
}

const form = ref({ ...defaultForm })

const formRules = {
  name: [{ required: true, message: '请输入规则名称', trigger: 'blur' }],
  metric: [{ required: true, message: '请选择指标', trigger: 'change' }],
  operator: [{ required: true, message: '请选择操作符', trigger: 'change' }],
  threshold: [{ required: true, message: '请输入阈值', trigger: 'blur' }],
  severity: [{ required: true, message: '请选择级别', trigger: 'change' }],
}

async function loadRules() {
  loading.value = true
  try {
    const res = await getAlertRules({ page_size: 100 })
    rules.value = res.results || res
  } catch { /* empty */ }
  loading.value = false
}

function handleAdd() {
  editingRule.value = null
  form.value = { ...defaultForm }
  dialogVisible.value = true
}

function handleEdit(row) {
  editingRule.value = row
  form.value = {
    name: row.name,
    metric: row.metric,
    operator: row.operator,
    threshold: row.threshold,
    duration: row.duration,
    severity: row.severity,
    cooldown: row.cooldown,
    enabled: row.enabled,
  }
  dialogVisible.value = true
}

async function handleSubmit() {
  const valid = await formRef.value?.validate().catch(() => false)
  if (!valid) return

  try {
    if (editingRule.value) {
      await updateAlertRule(editingRule.value.id, form.value)
      ElMessage.success('规则已更新')
    } else {
      await createAlertRule(form.value)
      ElMessage.success('规则已创建')
    }
    dialogVisible.value = false
    loadRules()
  } catch {
    ElMessage.error('保存失败')
  }
}

async function handleToggle(row) {
  try {
    await toggleAlertRule(row.id)
    ElMessage.success(row.enabled ? '已启用' : '已禁用')
  } catch {
    row.enabled = !row.enabled
    ElMessage.error('操作失败')
  }
}

async function handleDelete(row) {
  try {
    await ElMessageBox.confirm(`确定删除规则 "${row.name}" ？`, '提示', { type: 'warning' })
    await deleteAlertRule(row.id)
    ElMessage.success('已删除')
    loadRules()
  } catch { /* 取消 */ }
}

onMounted(() => {
  loadRules()
})
</script>

<style lang="scss" scoped>
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.condition-text {
  font-family: monospace;
  font-size: 13px;
  color: #409EFF;
}

.unit-label {
  margin-left: 8px;
  color: #909399;
  font-size: 13px;
}
</style>
