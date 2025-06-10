<template>
    <div class="task-form-container">
        <h2>{{ isEdit ? 'Редактирование задачи' : 'Новая задача' }}</h2>
        <form @submit.prevent="onSubmit">
            <div v-if="isEdit && form.issue_id">
                <label>ID задачи:</label>
                <input type="text" :value="form.issue_id" readonly />
            </div>
            <div>
                <label for="title">Заголовок:</label>
                <input
                    v-model="form.title"
                    type="text"
                    id="title"
                    placeholder="Укажите краткий заголовок"
                    required
                />
            </div>

            <div>
                <label for="description">Описание:</label>
                <textarea
                    v-model="form.description"
                    id="description"
                    placeholder="Подробное описание (опционально)"
                ></textarea>
            </div>

            <div>
                <label for="project">Проект:</label>
                <select v-model="form.project_id" id="project" required :disabled="isEdit">
                    <option disabled value="">-- выберите проект --</option>
                    <option
                        v-for="proj in projects"
                        :key="proj.id"
                        :value="proj.id"
                    >
                        {{ proj.name }}
                    </option>
                </select>
            </div>

            <div>
                <label for="due_date">Срок выполнения:</label>
                <input
                    v-model="form.due_date"
                    type="datetime-local"
                    id="due_date"
                />
            </div>

            <div>
                <label for="assignee">Исполнитель:</label>
                <select v-model="form.assignee" id="assignee">
                    <option :value="null">-- не назначен --</option>
                    <option
                        v-for="member in projectMembers"
                        :key="member.id"
                        :value="member.id"
                    >
                        {{ member.first_name }} {{ member.last_name }} ({{ member.email }})
                    </option>
                </select>
            </div>

            <div>
                <label for="status">Статус:</label>
                <select v-model="form.status" id="status" required>
                    <option disabled value="">-- выберите статус --</option>
                    <option
                        v-for="s in statuses"
                        :key="s.id"
                        :value="s.id"
                    >
                        {{ s.name }}
                    </option>
                </select>
            </div>

            <div>
                <label for="priority">Приоритет:</label>
                <select v-model="form.priority" id="priority" required>
                    <option disabled value="">-- выберите приоритет --</option>
                    <option
                        v-for="p in priorities"
                        :key="p.id"
                        :value="p.id"
                    >
                        {{ p.level }}
                    </option>
                </select>
            </div>

            <button type="submit">{{ isEdit ? 'Сохранить' : 'Создать' }}</button>
            <button @click="goBack" type="button">Отмена</button>
        </form>

        <p v-if="error" class="error">{{ error }}</p>
    </div>
</template>

<script>
import {computed, onMounted, ref, watch} from 'vue'
import {useAuthStore, useTaskStore} from '../store'
import {useRoute, useRouter} from 'vue-router'
import apiClient from '../services/api.js'

export default {
    name: 'TaskForm',
    setup() {
        const taskStore = useTaskStore()
        const authStore = useAuthStore()
        const route = useRoute()
        const router = useRouter()

        const isEdit = computed(() => Boolean(route.params.id))
        const taskId = computed(() => route.params.id)

        const form = ref({
            title: '',
            description: '',
            project_id: '',
            due_date: '',
            assignee: null,
            status: '',
            priority: ''
        })

        const statuses = computed(() => taskStore.statuses)
        const priorities = computed(() => taskStore.priorities)
        const projects = computed(() => taskStore.projects)

        const projectMembers = computed(() => {
            const proj = projects.value.find(p => p.id === form.value.project_id)
            return proj && proj.members ? proj.members : []
        })

        const error = ref('')

        onMounted(async () => {
            try {
                await authStore.fetchUser()
                await taskStore.fetchInitialData()
                if (isEdit.value) {
                    const response = await apiClient.get(`/tasks/tasks/${taskId.value}/?by_issue_id=1`)
                    const data = response.data
                    form.value.title = data.title || ''
                    form.value.description = data.description || ''
                    form.value.project_id = data.project?.id || ''
                    form.value.due_date = data.due_date ? data.due_date.slice(0, 16) : ''
                    form.value.assignee = data.assignee?.id || null
                    form.value.status = data.status || ''
                    form.value.priority = data.priority || ''
                    form.value.issue_id = data.issue_id
                } else {
                    if (projects.value.length > 0) {
                        form.value.project_id = projects.value[0].id
                    }
                    form.value.assignee = null
                }
            } catch (e) {
                console.error('Ошибка при инициализации формы:', e)
                error.value = 'Не удалось загрузить данные для формы.'
            }
        })

        async function onSubmit() {
            if (!form.value.title.trim()) {
                error.value = 'Укажите заголовок задачи'
                return
            }
            if (!form.value.project_id) {
                error.value = 'Выберите проект'
                return
            }
            if (!form.value.status) {
                error.value = 'Укажите статус'
                return
            }
            if (!form.value.priority) {
                error.value = 'Укажите приоритет'
                return
            }

            const payload = {
                title: form.value.title,
                description: form.value.description,
                project_id: form.value.project_id,
                due_date: form.value.due_date,
                assignee: form.value.assignee,
                status: form.value.status,
                priority: form.value.priority
            }

            try {
                if (isEdit.value) {
                    await taskStore.updateTask(taskId.value, payload, true)
                } else {
                    await taskStore.createTask(payload)
                }
                router.push({
                    name: 'TaskListByProject',
                    params: {projectId: form.value.project_id}
                })
            } catch (e) {
                console.error('Ошибка при сохранении задачи:', e)
                error.value = 'Не удалось сохранить задачу. Проверьте поля и попробуйте снова.'
            }
        }

        function goBack() {
            if (isEdit.value && form.value.project_id) {
                router.push({
                    name: 'TaskListByProject',
                    params: {projectId: form.value.project_id}
                })
            } else {
                router.push({name: 'ProjectList'})
            }
        }

        return {
            form,
            statuses,
            priorities,
            projects,
            isEdit,
            onSubmit,
            goBack,
            error,
            projectMembers
        }
    }
}
</script>

<style scoped>
.task-form-container {
    max-width: 500px;
    margin: 50px auto;
    padding: 0 20px;
}

.task-form-container div {
    margin-bottom: 15px;
}

.task-form-container input,
.task-form-container select,
.task-form-container textarea {
    width: 100%;
    padding: 8px;
    box-sizing: border-box;
}

button {
    margin-right: 10px;
    padding: 6px 12px;
    cursor: pointer;
}

.error {
    color: red;
    margin-top: 10px;
}
</style>
