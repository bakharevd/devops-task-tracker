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
                <tr v-for="project in filteredProjects" :key="project.id">
                    <td>
                        <router-link
                            :to="{
                                name: 'TaskListByProject',
                                params: { projectId: project.id },
                            }"
                        >
                            {{ project.name }}
                        </router-link>
                    </td>
                    <td>
                        <AvatarGroup>
                            <Avatar
                                v-for="user in project.members.slice(0, 4)"
                                :key="user.id"
                                :image="user.avatar_url"
                                shape="circle"
                                v-tooltip.top="`${user.last_name} ${user.first_name}\n(${user.position?.name || ''})`"
                            />
                            <Avatar 
                                v-if="project.members.length > 4"
                                :label="`+${project.members.length - 4}`"
                                shape="circle"
                                v-tooltip.top="extraUsernames(project.members)"
                            />
                        </AvatarGroup>
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
import { computed, onMounted, ref } from "vue";
import { useAuthStore, useTaskStore } from "../store";
import { useRouter } from "vue-router";

export default {
    name: "ProjectList",
    setup() {
        const taskStore = useTaskStore();
        const authStore = useAuthStore();
        const router = useRouter();
        const searchTerm = ref("");

        onMounted(async () => {
            await authStore.fetchUser();
            await taskStore.fetchProjects();
        });

        const filteredProjects = computed(() => {
            if (!searchTerm.value) {
                return taskStore.projects;
            }
            const s = searchTerm.value.toLowerCase();
            return taskStore.projects.filter(
                (p) =>
                    p.name.toLowerCase().includes(s) ||
                    p.description.toLowerCase().includes(s) ||
                    p.members.some((u) => u.username.toLowerCase().includes(s))
            );
        });

        function goCreateProject() {
            router.push({ name: "ProjectCreate" });
        }

        function goTasks() {
            router.push({ name: "TaskListAll" });
        }

        function goEdit(id) {
            router.push({ name: "ProjectEdit", params: { projectId: id } });
        }

        async function deleteProject(id) {
            if (confirm("Удалить проект? Все связанные задачи будут удалены")) {
                try {
                    await taskStore.deleteProject(id);
                } catch (e) {
                    console.error(e);
                }
            }
        }

        function extraUsernames(members) {
            const extra = members.slice(4)
            if (!extra.length) return ''
            return extra.map(u => `${u.last_name} ${u.first_name} (${u.position?.name || ''})`).join('\n')
        }

        return {
            searchTerm,
            filteredProjects,
            goCreateProject,
            goEdit,
            deleteProject,
            goTasks,
            extraUsernames,
        };
    },
};
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

th,
td {
    padding: 8px 12px;
    border: 1px solid #cccccc;
}

button {
    padding: 5px;
    cursor: pointer;
}
</style>
