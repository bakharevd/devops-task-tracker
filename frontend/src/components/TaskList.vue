<template>
    <div class="tasks-container">
        <h2>
            Задачи:
            <span v-if="projectName">{{ projectName }}</span>
            <span v-else>Все проекты</span>
        </h2>

        <div class="top-bar">
            <button @click="goCreate">Новая задача</button>
            <button @click="goProjects">Проекты</button>
            <input
                v-model="searchTerm"
                type="text"
                placeholder="Поиск задач..."
            />
        </div>

        <table>
            <thead>
            <tr>
                <th>Заголовок</th>
                <th v-if="!projectName">Проект</th>
                <th>Статус</th>
                <th>Приоритет</th>
                <th>Исполнитель</th>
                <th>Действия</th>
            </tr>
            </thead>
            <tbody>
            <tr
                v-for="task in filteredTasks"
                :key="task.id"
            >
                <td>{{ task.title }}</td>
                <td v-if="!projectName">{{ task.project.name }}</td>
                <td>{{ findStatusName(task.status) }}</td>
                <td>{{ findPriorityLevel(task.priority) }}</td>
                <td>{{ task.assignee || '—' }}</td>
                <td>
                    <button @click="goEdit(task.id)">✏️</button>
                    <button @click="onDelete(task.id)">🗑️</button>
                </td>
            </tr>
            </tbody>
        </table>

        <p v-if="!filteredTasks.length && tasks.length">Задачи не найдены.</p>
        <p v-if="!tasks.length">Нет задач для отображения.</p>
    </div>
</template>

<script>
import {computed, onMounted, ref} from 'vue'
import {useAuthStore, useTaskStore} from '../store'
import {useRoute, useRouter} from 'vue-router'

export default {
    name: 'TaskList',
    props: {
        projectId: {
            type: String,
            default: 'all'
        }
    },
    setup(props) {
        const taskStore = useTaskStore()
        const authStore = useAuthStore()
        const route = useRoute()
        const router = useRouter()
        const searchTerm = ref('')

        const tasks = computed(() => taskStore.tasks)
        const statuses = computed(() => taskStore.statuses)
        const priorities = computed(() => taskStore.priorities)
        const projects = computed(() => taskStore.projects)

        const projectName = computed(() => {
            if (props.projectId === 'all') return null
            const p = projects.value.find(pr => pr.id === Number(props.projectId))
            return p ? p.name : null
        })

        const filteredTasks = computed(() => {
            if (!searchTerm.value) {
                return tasks.value
            }
            return tasks.value.filter(task =>
                task.title.toLowerCase().includes(searchTerm.value.toLowerCase())
            )
        })

        onMounted(async () => {
            try {
                await authStore.fetchUser()
                await taskStore.fetchInitialData()
                await taskStore.fetchTasks(props.projectId)
            } catch (e) {
                console.error(e)
            }
        })

        function findStatusName(statusId) {
            const st = statuses.value.find(s => s.id === statusId)
            return st ? st.name : ''
        }

        function findPriorityLevel(priorityId) {
            const p = priorities.value.find(p => p.id === priorityId)
            return p ? p.level : ''
        }

        function goCreate() {
            router.push({name: 'TaskCreate'})
        }

        function goEdit(id) {
            router.push({name: 'TaskEdit', params: {id}})
        }

        async function onDelete(id) {
            if (confirm('Удалить задачу?')) {
                try {
                    await taskStore.deleteTask(id)
                } catch (e) {
                    console.error(e)
                }
            }
        }

        function goProjects() {
            router.push({name: 'ProjectList'})
        }

        return {
            tasks,
            projectName,
            filteredTasks,
            findStatusName,
            findPriorityLevel,
            searchTerm,
            goCreate,
            goEdit,
            onDelete,
            goProjects
        }
    }
}
</script>

<style scoped>
.tasks-container {
    max-width: 900px;
    margin: 50px auto;
    padding: 0 20px;
}

h2 {
    margin-bottom: 15px;
}

.top-bar {
    display: flex;
    align-items: center;
    gap: 10px;
    margin-bottom: 15px;
}

.top-bar input {
    flex-grow: 1;
    padding: 6px;
}

table {
    width: 100%;
    border-collapse: collapse;
}

th, td {
    padding: 8px 12px;
    border: 1px solid #ccc;
}

button {
    margin-right: 5px;
    cursor: pointer;
}
</style>
