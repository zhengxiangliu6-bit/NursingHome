<template>
  <div>
    <el-card>
      <template #header>
        <div class="card-header">
          <span>护理评估</span>
          <el-button type="primary" @click="dialogVisible = true">新建评估</el-button>
        </div>
      </template>
      <el-table :data="assessments" v-loading="loading" stripe>
        <el-table-column prop="resident_name" label="老人" width="100" />
        <el-table-column prop="assessor_name" label="评估人" width="100" />
        <el-table-column prop="assessment_date" label="评估日期" width="180" />
        <el-table-column prop="adl_score" label="ADL评分" width="90" />
        <el-table-column prop="cognitive_score" label="认知评分" width="90" />
        <el-table-column prop="mobility_score" label="行动评分" width="90" />
        <el-table-column prop="overall_score" label="综合评分" width="90" />
        <el-table-column prop="recommended_level_name" label="建议等级" width="100" />
        <el-table-column prop="status" label="状态" width="80">
          <template #default="{ row }">
            <el-tag :type="{ draft: 'info', submitted: 'warning', approved: 'success' }[row.status]" size="small">
              {{ { draft: '草稿', submitted: '已提交', approved: '已审核' }[row.status] }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="120">
          <template #default="{ row }">
            <el-button v-if="row.status === 'submitted'" type="success" size="small" @click="handleApprove(row.id)">审核</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-dialog v-model="dialogVisible" title="新建护理评估" width="600">
      <el-form :model="form" label-width="100px">
        <el-form-item label="老人">
          <el-select v-model="form.resident" filterable>
            <el-option v-for="r in residents" :key="r.id" :label="r.name" :value="r.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="ADL评分"><el-input-number v-model="form.adl_score" :min="0" :max="100" /></el-form-item>
        <el-form-item label="认知评分"><el-input-number v-model="form.cognitive_score" :min="0" :max="100" /></el-form-item>
        <el-form-item label="行动评分"><el-input-number v-model="form.mobility_score" :min="0" :max="100" /></el-form-item>
        <el-form-item label="综合评分"><el-input-number v-model="form.overall_score" :min="0" :max="100" /></el-form-item>
        <el-form-item label="建议等级">
          <el-select v-model="form.recommended_level">
            <el-option v-for="l in careLevels" :key="l.id" :label="l.name" :value="l.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="备注"><el-input v-model="form.notes" type="textarea" /></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit">保存并提交</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { getAssessments, createAssessment, approveAssessment, getResidents, getCareLevels } from '@/api/residents'
import { ElMessage } from 'element-plus'

const assessments = ref([])
const residents = ref([])
const careLevels = ref([])
const loading = ref(false)
const dialogVisible = ref(false)
const form = reactive({
  resident: '', assessment_date: new Date().toISOString(),
  adl_score: 80, cognitive_score: 80, mobility_score: 80, overall_score: 80,
  recommended_level: '', notes: '', status: 'submitted',
})

async function loadData() {
  loading.value = true
  try {
    const data = await getAssessments()
    assessments.value = data.results || data
  } finally { loading.value = false }
}

async function handleSubmit() {
  await createAssessment(form)
  ElMessage.success('评估已提交')
  dialogVisible.value = false
  loadData()
}

async function handleApprove(id) {
  await approveAssessment(id)
  ElMessage.success('审核通过')
  loadData()
}

onMounted(async () => {
  loadData()
  const [rData, clData] = await Promise.all([
    getResidents({ status: 'active', page_size: 100 }),
    getCareLevels(),
  ])
  residents.value = rData.results || rData
  careLevels.value = clData.results || clData
})
</script>

<style scoped>
.card-header { display: flex; justify-content: space-between; align-items: center; }
</style>
