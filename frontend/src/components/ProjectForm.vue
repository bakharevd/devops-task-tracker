<template>
    <div class="project-form-container">
        <h2>{{ isEdit ? 'Редактирование проекта' : 'Новый проект' }}</h2>
        <form @submit.prevent="onSubmit">
            <div>
                <label for="name">Название проекта:</label>
                <input
                    v-model="form.name"
                    type="text"
                    id="name"
                    placeholder="Введите название"
                    required
                />
            </div>

            <div>
                <label for="description">Описание:</label>
                <textarea
                    v-model="form.description"
                    id="description"
                    placeholder="Опционально: описание проекта"
                ></textarea>
            </div>

            <div>
                <label for="members">Участники проекта (для выбора нескольких элементов удерживайте Ctrl):</label>
                <select
                    v-model="form.members_ids"
                    id="members"
                    multiple
                    size="5"
                >
                    <option
                        v-for="user in users"
                        :key="user.id"
                        :value="user.id"
                    >
                        {{ user.username }} ({{ user.email }})
                    </option>
                </select>
            </div>

            <div>
                <label for="code">Код проекта:</label>
                <input
                    v-model="form.code"
                    type="text"
                    id="code"
                    placeholder="Короткий код (например, ASD)"
                    required
                />
            </div>

            <button type="submit">{{ isEdit ? 'Сохранить' : 'Создать' }}</button>
            <button @click="goBack" type="button">Отмена</button>
        </form>
        <p v-if="error" class="error">{{ error }}</p>
    </div>
</template>

<script>
import {computed, onMounted, ref} from 'vue'
import {useAuthStore, useTaskStore, useUserStore} from '../store'
import {useRoute, useRouter} from 'vue-router'
import apiClient from "../services/api";

export default {
    name: 'ProjectForm',
    setup() {
        const taskStore = useTaskStore()
        const userStore = useUserStore()
        const authStore = useAuthStore()
        const route = useRoute()
        const router = useRouter()

        const isEdit = computed(() => Boolean(route.params.projectId))
        const projectId = computed(() => route.params.projectId)

        const form = ref({
            name: '',
            description: '',
            members_ids: [],
            code: ''
        })
        const error = ref('')
        const users = computed(() => userStore.users)

        onMounted(async () => {
            try {
                await authStore.fetchUser()
                await userStore.fetchUsers()
                await taskStore.fetchProjects()

                if (isEdit.value) {
                    const response = await apiClient.get(`/tasks/projects/${projectId.value}/`)
                    const data = response.data
                    form.value.name = data.name || ''
                    form.value.description = data.description || ''
                    form.value.members_ids = data.members.map(u => u.id)
                    form.value.code = data.code || ''
                }
            } catch (e) {
                console.error('Ошибка при инициализации компонента:', e)
                error.value = 'Не удалось загрузить данные формы'
            }
        })

        async function onSubmit() {
            if (!form.value.name.trim()) {
                error.value = 'Укажите название проекта'
                return
            }
            const payload = {
                name: form.value.name,
                description: form.value.description,
                members_ids: form.value.members_ids,
                code: form.value.code
            }
            try {
                if (isEdit.value) {
                    await taskStore.updateProject(projectId.value, payload)
                } else {
                    await taskStore.createProject(payload)
                }
                router.push({ name: 'ProjectList' })
            } catch (err) {
                console.error('Ошибка при сохранении проекта:', err)
                error.value = 'Не удалось сохранить проект'
            }
        }

        function goBack() {
            router.push({name: 'ProjectList'})
        }

        return {
            form,
            users,
            isEdit,
            onSubmit,
            goBack,
            error,
        }
    }
}
</script>

<style scoped>
.project-form-container {
    max-width: 500px;
    margin: 50px auto;
    padding: 0 20px;
}

.project-form-container div {
    margin-bottom: 15px;
}

.project-form-container input,
.project-form-container select,
.project-form-container textarea {
    width: 100%;
    padding: 8px;
    box-sizing: border-box;
}

select[multiple] {
    height: 120px;
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

