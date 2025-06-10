<template>
    <div class="min-h-screen flex flex-col items-center justify-center px-4">
        <h1 class="text-2xl font-semibold mb-6 mt-6">
            <span v-if="projectName">{{ projectName }}</span>
            <span v-else>Все проекты</span>
        </h1>

        <div class="top-bar">
            <button @click="goCreate">Новая задача</button>
            <button @click="goProjects">Проекты</button>
            <input
                v-model="searchTerm"
                type="text"
                placeholder="Поиск задач..."
            />
        </div>

        <p v-if="!filteredTasks.length && tasks.length">Задачи не найдены.</p>
        <p v-if="!tasks.length">Нет задач для отображения.</p>

        <DataTable :value="filteredTasks" class="w-full max-w-7xl" responsiveLayout="scroll">
            <Column field="issue_id" header="ID" sortable>
                <template #body="slotProps">
                    <router-link :to="{ name: 'TaskDetail', params: { id: slotProps.data.issue_id } }">
                        {{ slotProps.data.issue_id }}
                    </router-link>
                </template>
            </Column>
            <Column field="title" header="Название" sortable>
                <template #body="slotProps">
                    <router-link :to="{ name: 'TaskDetail', params: { id: slotProps.data.issue_id } }">
                        {{ slotProps.data.title }}
                    </router-link>
                </template>
            </Column>
            <Column field="project.name" header="Проект" sortable>
                <template #body="slotProps">
                    <router-link :to="{ name: 'TaskListByProject', params: { projectId: slotProps.data.project.id } }">
                        {{ slotProps.data.project.name }}
                    </router-link>
                </template>
            </Column>
            <Column field="assignee.username" header="Исполнитель" sortable>
                <template #body="slotProps">
                    <div v-if="slotProps.data.assignee"
                        class="flex items-center gap-2"
                        v-tooltip.top="`${slotProps.data.assignee?.email}\n(${slotProps.data.assignee?.position?.name || ''})`"
                    >
                        <Avatar
                            :image="slotProps.data.assignee?.avatar_url"
                            shape="circle"
                        />
                        {{ slotProps.data.assignee?.last_name + " " + slotProps.data.assignee?.first_name || "—" }}
                    </div>
                </template>
            </Column>
            <Column field="priority" header="Приоритет" sortable>
                <template #body="slotProps">
                    <div class="w-full text-center">
                        <Tag 
                            v-if="findPriorityLevel(slotProps.data.priority)"
                            :severity="uiStyles.getPriorityStyle(findPriorityLevel(slotProps.data.priority)).severity"
                            :icon="uiStyles.getPriorityStyle(findPriorityLevel(slotProps.data.priority)).icon"
                            rounded
                        />
                    </div>
                </template>
            </Column>
            <Column field="status" header="Статус" sortable>
                <template #body="slotProps">
                    <div class="w-full text-center">
                        <Tag 
                            v-if="findStatusName(slotProps.data.status)"
                            :severity="uiStyles.getStatusStyle(findStatusName(slotProps.data.status)).severity"
                            :value="uiStyles.getStatusStyle(findStatusName(slotProps.data.status)).label"
                            :icon="uiStyles.getStatusStyle(findStatusName(slotProps.data.status)).icon"
                        />
                    </div>
                </template>
            </Column>
            <Column header="">
                <template #body="slotProps">
                    <div class="flex">
                        <Button class="m-1" @click="goEdit(slotProps.data.issue_id)" icon="pi pi-pencil" severity="info" variant="text" raised rounded  />
                        <Button class="m-1" @click="onDelete(slotProps.data.issue_id)" icon="pi pi-trash" severity="danger" variant="text" raised rounded  />
                    </div>
                </template>
            </Column>
        </DataTable>
    </div>
</template>

<script>
import { computed, onMounted, ref, watch } from "vue";
import { useAuthStore, useTaskStore } from "../store";
import { useUiStyleStore } from "../store/uiStyles";
import { useRouter, useRoute } from "vue-router";

export default {
    name: "TaskList",
    props: {
        projectId: {
            type: String,
            default: "all",
        },
    },
    setup(props) {
        const taskStore = useTaskStore();
        const authStore = useAuthStore();
        const uiStyles = useUiStyleStore();
        const router = useRouter();
        const route = useRoute();
        const searchTerm = ref("");

        const tasks = computed(() => taskStore.tasks);
        const statuses = computed(() => taskStore.statuses);
        const priorities = computed(() => taskStore.priorities);
        const projects = computed(() => taskStore.projects);

        const projectName = computed(() => {
            if (props.projectId === "all") return null;
            const p = projects.value.find(
                (pr) => pr.id === Number(props.projectId)
            );
            return p ? p.name : null;
        });

        const filteredTasks = computed(() => {
            if (!searchTerm.value) {
                return tasks.value;
            }
            return tasks.value.filter((task) =>
                task.title
                    .toLowerCase()
                    .includes(searchTerm.value.toLowerCase())
            );
        });

        onMounted(async () => {
            try {
                await authStore.fetchUser();
                await taskStore.fetchInitialData();
                await taskStore.fetchTasks(
                    route.params.projectId || props.projectId
                );
            } catch (e) {
                console.error(e);
            }
        });

        watch(
            () => route.params.projectId,
            async (newId) => {
                await taskStore.fetchTasks(newId || "all");
            }
        );

        function findStatusName(statusId) {
            const st = statuses.value.find((s) => s.id === statusId);
            return st ? st.name : "";
        }

        function findPriorityLevel(priorityId) {
            const p = priorities.value.find((p) => p.id === priorityId);
            return p ? p.level : "";
        }

        function goCreate() {
            router.push({ name: "TaskCreate" });
        }

        function goEdit(id) {
            router.push({ name: "TaskEdit", params: { id } });
        }

        async function onDelete(id) {
            if (confirm("Удалить задачу?")) {
                try {
                    await taskStore.deleteTask(id);
                } catch (e) {
                    console.error(e);
                }
            }
        }

        function goProjects() {
            router.push({ name: "ProjectList" });
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
            goProjects,
            uiStyles,
        };
    },
};
</script>
