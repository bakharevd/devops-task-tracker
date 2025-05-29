<template>
    <div class="task-form-container">
        <h2>{{ isEdit ? 'Редактирование задачи' : 'Новая задача' }}</h2>
        <form @submit.prevent="onSubmit">
            <div>
                <label for="title">Заголовок:</label>
                <input v-model="form.title" type="text" id="title" required/>
            </div>
            <div>
                <label for="description">Описание:</label>
                <textarea v-model="form.description" id="description"></textarea>
            </div>
            <div>
                <label for="due_date">Срок выполнения:</label>
                <input v-model="form.due_date" type="datetime-local" id="due_date"/>
            </div>
            <div>
                <label for="assignee">Исполнитель (User ID):</label>
                <input v-model="form.assignee" type="number" id="assignee"/>
            </div>
            <div>
                <label for="status">Статус:</label>
                <select v-model="form.status" id="status" required>
                    <option v-for="s in statuses" :key="s.id" :value="s.id">
                        {{ s.name }}
                    </option>
                </select>
            </div>
            <div>
                <label for="priority">Приоритет:</label>
                <select v-model="form.priority" id="priority" required>
                    <option v-for="p in priorities" :key="p.id" :value="p.id">
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
import {useAuthStore, useTaskStore} from '../store'
import {computed, onMounted, ref} from 'vue'
import {useRouter} from "vue-router";

export default {
    name: 'TaskForm',
    props: {},
    setup(props, {emit}) {
        const taskStore = useTaskStore()
        const authStore = useAuthStore()
        const route = useRouter().currentRoute

        const isEdit = computed(() => !!route.value.params.id)
        const taskId = computed(() => route.value.params.id)

        const form = ref({
            title: '',
            description: '',
            due_date: '',
            assignee: null,
            status: null,
            priority: null
        })

        const statuses = computed(() => taskStore.statuses)
        const priorities = computed(() => taskStore.priorities)
        const error = ref('')

        onMounted(async () => {
            try {
                await authStore.fetchUser()
                await taskStore.fetchInitialData()
                if (isEdit.value) {
                    const taskResponse = await fetch(
                        `${import.meta.env.VUE_APP_API_URL}/tasks/tasks/${taskId.value}/`,
                        {
                            headers: {
                                Authorization: `Bearer ${authStore.accessToken}`
                            }
                        }
                    )
                    if (!taskResponse.ok) {
                        throw new Error('Не удалось получить данные задачи')
                    }
                    const data = await taskResponse.json()
                    form.value = {
                        title: data.title,
                        description: data.description,
                        due_date: data.due_date
                            ? data.due_date.slice(0, 16)
                            : '',
                        assignee: data.assignee,
                        status: data.status,
                        priority: data.priority
                    }
                }
            } catch (e) {
                console.error(e)
            }
        })

        async function onSubmit() {
            try {
                if (isEdit.value) {
                    await taskStore.updateTask(taskId.value, {
                        title: form.value.title,
                        description: form.value.description,
                        due_date: form.value.due_date,
                        assignee: form.value.assignee,
                        status: form.value.status,
                        priority: form.value.priority
                    })
                } else {
                    await taskStore.createTask({
                        title: form.value.title,
                        description: form.value.description,
                        due_date: form.value.due_date,
                        assignee: form.value.assignee,
                        status: form.value.status,
                        priority: form.value.priority
                    })
                }
                window.location = '/tasks'
            } catch (err) {
                error.value = 'Ошибка при сохранении задачи'
                console.error(err)
            }
        }

        function goBack() {
            window.location = '/tasks'
        }

        return {
            form,
            statuses,
            priorities,
            isEdit,
            onSubmit,
            error,
            goBack
        }
    }
}
</script>

<style scoped>
.task-form-container {
    width: 500px;
    margin: 50px auto;
}

.task-form-container div {
    margin-bottom: 15px;
}

.error {
    color: red;
    margin-top: 10px;
}
</style>
