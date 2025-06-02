<template>
    <div class="projects-container">
        <h2>Проекты</h2>

        <div class="search-block">
            <input
                v-model="searchTerm"
                type="text"
                placeholder="Поиск проектов..."
            />
        </div>

        <div class="actions">
            <button @click="goCreateProject">+ Новый проект</button>
            <button @click="goTasks">Все задачи</button>
        </div>

        <table v-if="filteredProjects.length">
            <thead>
            <tr>
                <th>Название</th>
                <th>Участники</th>
                <th>Действия</th>
            </tr>
            </thead>
            <tbody>
            <tr
                v-for="project in filteredProjects"
                :key="project.id"
            >
                <td>
                    <router-link :to="{name: 'TaskListByProject', params: {projectId: project.id} }">
                        {{ project.name }}
                    </router-link>
                </td>
                <td>
                    {{ project.members.map(u => u.username).join(', ') || '-' }}
                </td>
                <td>
                    <button @click="goEdit(project.id)">✏️</button>
                    <button @click="deleteProject(project.id)">🗑️</button>
                </td>
            </tr>
            </tbody>
        </table>
        <p v-else>Проекты не найдены</p>
    </div>
</template>

<script>
import {computed, onMounted, ref} from 'vue'
import {useAuthStore, useTaskStore} from '../store'
import {useRouter} from 'vue-router'

export default {
    name: 'ProjectList',
    setup() {
        const taskStore = useTaskStore()
        const authStore = useAuthStore()
        const router = useRouter()
        const searchTerm = ref('')

        onMounted(async () => {
            await authStore.fetchUser()
            await taskStore.fetchProjects()
        })

        const filteredProjects = computed(() => {
            if (!searchTerm.value) {
                return taskStore.projects
            }
            const s = searchTerm.value.toLowerCase()
            return taskStore.projects.filter(
                p =>
                    p.name.toLowerCase().includes(s) ||
                    p.description.toLowerCase().includes(s) ||
                    p.members.some(u => u.username.toLowerCase().includes(s))
            )
        })

        function goCreateProject() {
            router.push({name: 'ProjectCreate'})
        }

        function goTasks() {
            router.push({name: 'TaskListAll'})
        }

        function goEdit(id) {
            router.push({name: 'ProjectEdit', params: {projectId: id}})
        }

        async function deleteProject(id) {
            if (confirm('Удалить проект? Все связанные задачи будут удалены')) {
                try {
                    await taskStore.deleteProject(id)
                } catch (e) {
                    console.error(e)
                }
            }
        }

        return {
            searchTerm,
            filteredProjects,
            goCreateProject,
            goEdit,
            deleteProject,
            goTasks,
        }
    }
}
</script>

<style scoped>
.projects-container {
    max-width: 800px;
    margin: 30px auto;
    padding: 0 20px;
}

.search-block {
    margin-bottom: 10px;
}

.search-block input {
    width: 100%;
    padding: 8px;
}

.actions {
    margin-bottom: 15px;
}

table {
    width: 100%;
    border-collapse: collapse;
}

th, td {
    padding: 8px 12px;
    border: 1px solid #cccccc;
}

button {
    padding: 5px;
    cursor: pointer;
}
</style>
