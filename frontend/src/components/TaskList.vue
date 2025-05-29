<template>
    <div class="tasks-container">
        <h2>Список задач</h2>
        <button @click="goCreate">Новая задача</button>
        <table>
            <thead>
            <tr>
                <th>Заголовок</th>
                <th>Статус</th>
                <th>Приоритет</th>
                <th>Исполнитель</th>
                <th>Действия</th>
            </tr>
            </thead>
            <tbody>
            <tr v-for="task in tasks" :key="task.id">
                <td>{{ task.title }}</td>
                <td>{{ findStatusName(task.status) }}</td>
                <td>{{ findPriorityLevel(task.priority) }}</td>
                <td>{{ task.assignee }}</td>
                <td>
                    <button @click="goEdit(task.id)">Редактировать</button>
                    <button @click="onDelete(task.id)">Удалить</button>
                </td>
            </tr>
            </tbody>
        </table>
    </div>
</template>

<script>
import {useAuthStore, useTaskStore} from "../store";
import {computed, onMounted} from "vue";

export default {
    name: 'TaskList',
    setup() {
        const taskStore = useTaskStore()
        const authStore = useAuthStore()

        const tasks = computed(() => taskStore.tasks)
        const statuses = computed(() => taskStore.statuses)
        const priorities = computed(() => taskStore.priorities)

        onMounted(async () => {
            try {
                await authStore.fetchUser()
                await taskStore.fetchInitialData()
                await taskStore.fetchTasks()
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
            window.location = '/tasks/new'
        }

        function goEdit(id) {
            window.location = `/tasks/${id}/edit`
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

        return {
            tasks,
            findStatusName,
            findPriorityLevel,
            goCreate,
            goEdit,
            onDelete
        }
    }
}
</script>

<style scoped>
.tasks-container {
    max-width: 800px;
    margin: 50px auto;
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
}
</style>