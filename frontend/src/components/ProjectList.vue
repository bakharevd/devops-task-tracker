<template>
    <div class="min-h-screen flex flex-col items-center px-4 inset-x-0 top-0">
        <h1 class="text-2xl font-semibold mb-6 mt-6">Проекты</h1>

        <div class="card w-full max-w-7xl">
            <div class="flex items-center gap-3 mb-4">
                <div class="p-input-icon-left flex-1">
                    <InputText
                        v-model="searchTerm"
                        type="text"
                        placeholder="Поиск по названию, описанию или участникам..."
                        class="w-full"
                    />
                </div>
                <div class="flex gap-2">
                    <Button
                        @click="goCreateProject"
                        severity="success"
                        rounded
                        raised
                        class="flex items-center gap-2"
                    >
                        <i class="pi pi-plus"></i>
                        <span>Новый проект</span>
                    </Button>
                </div>
            </div>

            <div v-if="loading" class="mt-4">
                <div v-for="i in 5" :key="i" class="mb-4">
                    <Skeleton height="2rem" class="mb-2" />
                    <Skeleton height="2rem" class="mb-2" />
                    <Skeleton height="2rem" />
                </div>
            </div>

            <div v-else-if="!filteredProjects.length" class="text-center text-gray-500 py-4">
                <p v-if="taskStore.projects.length">Проекты не найдены</p>
                <p v-else>Нет проектов для отображения</p>
            </div>

            <DataTable
                v-else
                :value="filteredProjects"
                responsiveLayout="scroll"
                class="mt-2"
                paginator
                :rows="10"
                :rowsPerPageOptions="[5, 10, 20, 50]"
            >
                <Column field="name" header="Название" sortable>
                    <template #body="slotProps">
                        <router-link
                            :to="{
                                name: 'TaskListByProject',
                                params: { projectId: slotProps.data.id },
                            }"
                            class="text-primary hover:underline"
                        >
                            {{ slotProps.data.name }}
                        </router-link>
                    </template>
                </Column>
                <Column field="members" header="Участники">
                    <template #body="slotProps">
                        <AvatarGroup>
                            <Avatar
                                v-for="user in slotProps.data.members.slice(0, 4)"
                                :key="user.id"
                                :image="user.avatar_url"
                                shape="circle"
                                v-tooltip.top="`${user.last_name} ${user.first_name}\n(${user.position?.name || ''})`"
                            />
                            <Avatar 
                                v-if="slotProps.data.members.length > 4"
                                :label="`+${slotProps.data.members.length - 4}`"
                                shape="circle"
                                v-tooltip.top="extraUsernames(slotProps.data.members)"
                            />
                        </AvatarGroup>
                    </template>
                </Column>
                <Column header="Действия" headerClass="text-center">
                    <template #body="slotProps">
                        <div class="flex justify-center">
                            <Button
                                class="m-1"
                                @click="goEdit(slotProps.data.id)"
                                icon="pi pi-pencil"
                                severity="info"
                                variant="text"
                                raised
                                rounded
                            />
                            <Button
                                class="m-1"
                                @click="deleteProject(slotProps.data.id)"
                                icon="pi pi-trash"
                                severity="danger"
                                variant="text"
                                raised
                                rounded
                            />
                        </div>
                    </template>
                </Column>
            </DataTable>
        </div>
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
        const loading = ref(true);

        onMounted(async () => {
            try {
                loading.value = true;
                await authStore.fetchUser();
                await taskStore.fetchProjects();
            } catch (e) {
                console.error(e);
            } finally {
                loading.value = false;
            }
        });

        const filteredProjects = computed(() => {
            if (!searchTerm.value) {
                return taskStore.projects;
            }
            const s = searchTerm.value.toLowerCase();
            return taskStore.projects.filter(
                (p) =>
                    p.name.toLowerCase().includes(s) ||
                    p.description?.toLowerCase().includes(s) ||
                    p.members.some((u) => 
                        u.username.toLowerCase().includes(s) ||
                        `${u.last_name} ${u.first_name}`.toLowerCase().includes(s)
                    )
            );
        });

        function goCreateProject() {
            router.push({ name: "ProjectCreate" });
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
            extraUsernames,
            taskStore,
            loading
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
