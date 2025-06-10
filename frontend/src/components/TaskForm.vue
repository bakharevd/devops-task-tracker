<template>
    <div class="min-h-screen flex flex-col items-center px-4 inset-x-0 top-0">
        <div class="card w-full max-w-3xl mt-8">
            <div class="flex justify-between items-center mb-6">
                <div class="flex items-center gap-4">
                    <Button
                        @click="goBack"
                        icon="pi pi-arrow-left"
                        severity="secondary"
                        text
                        rounded
                        raised
                    />
                    <h2 class="text-2xl font-semibold m-0">
                        {{ isEdit ? 'Редактирование задачи' : 'Новая задача' }}
                    </h2>
                </div>
            </div>

            <form @submit.prevent="onSubmit" class="flex flex-col gap-6">
                <div v-if="isEdit && form.issue_id" class="field">
                    <label class="block text-sm font-medium text-gray-600 mb-1">ID задачи</label>
                    <InputText :value="form.issue_id" readonly />
                </div>

                <div class="field">
                    <label for="title" class="block text-sm font-medium text-gray-600 mb-1">Заголовок</label>
                    <InputText
                        v-model="form.title"
                        id="title"
                        placeholder="Укажите краткий заголовок"
                        class="w-full"
                        required
                    />
                </div>

                <div class="field">
                    <label for="description" class="block text-sm font-medium text-gray-600 mb-1">Описание</label>
                    <Editor
                        v-model="form.description"
                        editorStyle="height: 200px"
                        :pt="{
                            toolbar: { class: 'border-none' },
                            content: { class: 'border border-gray-300 rounded-lg' }
                        }"
                    />
                </div>

                <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div class="field">
                        <label for="project" class="block text-sm font-medium text-gray-600 mb-1">Проект</label>
                        <Dropdown
                            v-model="form.project_id"
                            :options="projects"
                            optionLabel="name"
                            optionValue="id"
                            placeholder="Выберите проект"
                            class="w-full"
                            :disabled="isEdit"
                            required
                        />
                    </div>

                    <div class="field">
                        <label for="due_date" class="block text-sm font-medium text-gray-600 mb-1">Срок выполнения</label>
                        <Calendar
                            v-model="form.due_date"
                            showTime
                            hourFormat="24"
                            class="w-full"
                        />
                    </div>

                    <div class="field">
                        <label for="assignee" class="block text-sm font-medium text-gray-600 mb-1">Исполнитель</label>
                        <Dropdown
                            v-model="form.assignee"
                            :options="projectMembers"
                            optionLabel="fullName"
                            optionValue="id"
                            placeholder="Не назначен"
                            class="w-full"
                        >
                            <template #option="slotProps">
                                <div class="flex items-center gap-2">
                                    <Avatar
                                        :image="slotProps.option.avatar_url"
                                        shape="circle"
                                        size="small"
                                    />
                                    <span>{{ slotProps.option.fullName }}</span>
                                </div>
                            </template>
                        </Dropdown>
                    </div>

                    <div class="field">
                        <label for="status" class="block text-sm font-medium text-gray-600 mb-1">Статус</label>
                        <Dropdown
                            v-model="form.status"
                            :options="statuses"
                            optionLabel="name"
                            optionValue="id"
                            placeholder="Выберите статус"
                            class="w-full"
                            required
                        />
                    </div>

                    <div class="field">
                        <label for="priority" class="block text-sm font-medium text-gray-600 mb-1">Приоритет</label>
                        <Dropdown
                            v-model="form.priority"
                            :options="priorities"
                            optionLabel="level"
                            optionValue="id"
                            placeholder="Выберите приоритет"
                            class="w-full"
                            required
                        />
                    </div>
                </div>

                <div class="flex justify-end gap-2 mt-4">
                    <Button
                        type="button"
                        @click="goBack"
                        label="Отмена"
                        severity="secondary"
                        outlined
                    />
                    <Button
                        type="submit"
                        :label="isEdit ? 'Сохранить' : 'Создать'"
                        severity="success"
                        :loading="loading"
                    />
                </div>
            </form>

            <Message v-if="error" severity="error" :closable="false" class="mt-4">
                {{ error }}
            </Message>
        </div>
    </div>
</template>

<script>
import { computed, onMounted, ref, watch } from 'vue'
import { useAuthStore, useTaskStore } from '../store'
import { useRoute, useRouter } from 'vue-router'
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
            const members = proj && proj.members ? proj.members : []
            return members.map(member => ({
                ...member,
                fullName: `${member.last_name} ${member.first_name}`
            }))
        })

        const error = ref('')
        const loading = ref(false)

        onMounted(async () => {
            loading.value = true
            try {
                await authStore.fetchUser()
                await taskStore.fetchInitialData()
                if (isEdit.value) {
                    const response = await apiClient.get(`/tasks/tasks/${taskId.value}/?by_issue_id=1`)
                    const data = response.data
                    form.value.title = data.title || ''
                    form.value.description = data.description || ''
                    form.value.project_id = data.project?.id || ''
                    form.value.due_date = data.due_date || ''
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
                if (e.response) {
                    error.value = e.response.data.detail || 'Не удалось загрузить данные для формы'
                } else if (e.request) {
                    error.value = 'Нет ответа от сервера'
                } else {
                    error.value = 'Не удалось загрузить данные для формы'
                }
            } finally {
                loading.value = false
            }
        })

        const handleSubmit = async () => {
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

            loading.value = true
            error.value = ''
            try {
                const payload = {
                    title: form.value.title,
                    description: form.value.description || '',
                    project_id: parseInt(form.value.project_id),
                    due_date: form.value.due_date || null,
                    assignee_id: form.value.assignee || null,
                    status: parseInt(form.value.status),
                    priority: parseInt(form.value.priority)
                }
                
                if (isEdit.value) {
                    await taskStore.updateTask(taskId.value, payload, true)
                    router.push({
                        name: 'TaskDetail',
                        params: { id: taskId.value }
                    })
                } else {
                    const response = await taskStore.createTask(payload)
                    console.log('Response from createTask:', response)
                    
                    if (!response?.data?.issue_id) {
                        throw new Error('Не удалось получить ID созданной задачи')
                    }

                    router.push({
                        name: 'TaskDetail',
                        params: { id: response.data.issue_id }
                    })
                }
            } catch (e) {
                console.error('Ошибка при сохранении задачи:', e)
                if (e.response) {
                    error.value = e.response.data.detail || 'Не удалось сохранить задачу'
                } else if (e.request) {
                    error.value = 'Нет ответа от сервера'
                } else {
                    error.value = e.message || 'Не удалось сохранить задачу'
                }
            } finally {
                loading.value = false
            }
        }

        function goBack() {
            if (isEdit.value) {
                router.push({
                    name: 'TaskDetail',
                    params: { id: taskId.value }
                })
            } else if (form.value.project_id) {
                router.push({
                    name: 'TaskListByProject',
                    params: { projectId: form.value.project_id }
                })
            } else {
                router.push({ name: 'ProjectList' })
            }
        }

        return {
            form,
            statuses,
            priorities,
            projects,
            isEdit,
            onSubmit: handleSubmit,
            goBack,
            error,
            projectMembers,
            loading
        }
    }
}
</script>

<style scoped>
.field {
    display: flex;
    flex-direction: column;
    gap: 0.25rem;
}
</style>
