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
        </div>

        <ul v-if="filteredProjects.length">
            <li>
                <router-link :to="{ name: 'TaskListAll' }">
                    Все проекты
                </router-link>
            </li>
            <li
                v-for="project in filteredProjects"
                :key="project.id"
            >
                <router-link
                    :to="{ name: 'TaskListByProject', params: { projectId: project.id } }"
                >
                    {{ project.name }}
                </router-link>
            </li>
        </ul>
        <p v-else>Проекты не найдены.</p>
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
            return taskStore.projects.filter(proj =>
                proj.name.toLowerCase().includes(searchTerm.value.toLowerCase())
            )
        })

        function goCreateProject() {
            router.push({name: 'ProjectCreate'})
        }

        return {
            searchTerm,
            filteredProjects,
            goCreateProject
        }
    }
}
</script>

<style scoped>
.projects-container {
    max-width: 600px;
    margin: 30px auto;
    padding: 0 20px;
}

h2 {
    margin-bottom: 15px;
}

.search-block {
    margin-bottom: 10px;
}

.search-block input {
    width: 100%;
    padding: 8px;
    box-sizing: border-box;
}

.actions {
    margin-bottom: 15px;
}

ul {
    list-style: none;
    padding: 0;
}

li {
    margin: 8px 0;
}

button {
    padding: 6px 12px;
    cursor: pointer;
}
</style>
