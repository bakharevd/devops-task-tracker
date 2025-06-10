<template>
    <div class="min-h-screen flex flex-col items-center px-4 inset-x-0 top-0">
        <h1 class="text-2xl font-semibold mb-6 mt-6">
            <span v-if="projectName">{{ projectName }}</span>
            <span v-else>Все проекты</span>
        </h1>

        <div class="card w-full max-w-7xl">
            <Tabs :value="activeTab" @update:value="onTabChange">
                <TabList>
                    <Tab
                        v-for="tab in tabs"
                        :key="tab.value"
                        :value="tab.value"
                    >
                        <div class="flex items-center gap-2">
                            <i :class="tab.icon" />
                            <span>{{ tab.label }}</span>
                        </div>
                    </Tab>
                </TabList>
                <TabPanels>
                    <TabPanel
                        v-for="tab in tabs"
                        :key="tab.value"
                        :value="tab.value"
                    >
                        <div class="flex items-center gap-3 mb-4">
                            <div class="p-input-icon-left flex-1">
                                <InputText
                                    v-model="searchTerm"
                                    type="text"
                                    placeholder="Поиск по ID, названию, исполнителю или статусу..."
                                    class="w-9/10"
                                />
                            </div>
                            <Button
                                @click="goCreate"
                                severity="success"
                                rounded
                                raised
                                class="flex items-center gap-2"
                            >
                                <i class="pi pi-plus"></i>
                                <span>Новая задача</span>
                            </Button>
                        </div>

                        <div v-if="loading" class="mt-4">
                            <div v-for="i in 5" :key="i" class="mb-4">
                                <Skeleton height="2rem" class="mb-2" />
                                <Skeleton height="2rem" class="mb-2" />
                                <Skeleton height="2rem" />
                            </div>
                        </div>

                        <div
                            v-else-if="!getFilteredTasksByTab(activeTab).length"
                            class="text-center text-gray-500 py-4"
                        >
                            <p v-if="tasks.length">Задачи не найдены</p>
                            <p v-else>Нет задач для отображения</p>
                        </div>

                        <DataTable
                            v-else
                            :value="getFilteredTasksByTab(activeTab)"
                            responsiveLayout="scroll"
                            class="mt-2"
                            paginator
                            :rows="10"
                            :rowsPerPageOptions="[5, 10, 20, 50]"
                        >
                            <Column
                                field="issue_id"
                                header="ID"
                                sortable
                            >
                                <template #body="slotProps">
                                    <router-link
                                        :to="{
                                            name: 'TaskDetail',
                                            params: {
                                                id: slotProps.data.issue_id,
                                            },
                                        }"
                                    >
                                        {{ slotProps.data.issue_id }}
                                    </router-link>
                                </template>
                            </Column>
                            <Column
                                field="title"
                                header="Название"
                                sortable
                            >
                                <template #body="slotProps">
                                    <router-link
                                        :to="{
                                            name: 'TaskDetail',
                                            params: {
                                                id: slotProps.data.issue_id,
                                            },
                                        }"
                                    >
                                        {{ slotProps.data.title }}
                                    </router-link>
                                </template>
                            </Column>
                            <Column
                                field="assignee.username"
                                header="Исполнитель"
                                sortable
                            >
                                <template #body="slotProps">
                                    <div
                                        v-if="slotProps.data.assignee"
                                        class="flex items-center gap-2"
                                        v-tooltip.top="
                                            `${
                                                slotProps.data.assignee?.email
                                            }\n(${
                                                slotProps.data.assignee
                                                    ?.position?.name || ''
                                            })`
                                        "
                                    >
                                        <Avatar
                                            :image="
                                                slotProps.data.assignee
                                                    ?.avatar_url
                                            "
                                            shape="circle"
                                        />
                                        {{
                                            slotProps.data.assignee?.last_name +
                                                " " +
                                                slotProps.data.assignee
                                                    ?.first_name || "—"
                                        }}
                                    </div>
                                </template>
                            </Column>
                            <Column
                                field="priority"
                                header="Приоритет"
                                sortable
                            >
                                <template #body="slotProps">
                                    <div class="w-full text-center">
                                        <Tag
                                            v-if="
                                                findPriorityLevel(
                                                    slotProps.data.priority
                                                )
                                            "
                                            :severity="
                                                uiStyles.getPriorityStyle(
                                                    findPriorityLevel(
                                                        slotProps.data.priority
                                                    )
                                                ).severity
                                            "
                                            :icon="
                                                uiStyles.getPriorityStyle(
                                                    findPriorityLevel(
                                                        slotProps.data.priority
                                                    )
                                                ).icon
                                            "
                                            rounded
                                        />
                                    </div>
                                </template>
                            </Column>
                            <Column
                                field="status"
                                header="Статус"
                                headerClass="flex justify-center"
                                sortable
                            >
                                <template #body="slotProps">
                                    <div class="w-full text-center">
                                        <Tag
                                            v-if="
                                                findStatusName(
                                                    slotProps.data.status
                                                )
                                            "
                                            :severity="
                                                uiStyles.getStatusStyle(
                                                    findStatusName(
                                                        slotProps.data.status
                                                    )
                                                ).severity
                                            "
                                            :value="
                                                uiStyles.getStatusStyle(
                                                    findStatusName(
                                                        slotProps.data.status
                                                    )
                                                ).label
                                            "
                                            :icon="
                                                uiStyles.getStatusStyle(
                                                    findStatusName(
                                                        slotProps.data.status
                                                    )
                                                ).icon
                                            "
                                        />
                                    </div>
                                </template>
                            </Column>
                            <Column header="">
                                <template #body="slotProps">
                                    <div class="flex">
                                        <Button
                                            class="m-1"
                                            @click="
                                                goEdit(slotProps.data.issue_id)
                                            "
                                            icon="pi pi-pencil"
                                            severity="info"
                                            variant="text"
                                            raised
                                            rounded
                                        />
                                        <Button
                                            class="m-1"
                                            @click="
                                                onDelete(
                                                    slotProps.data.issue_id
                                                )
                                            "
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
                    </TabPanel>
                </TabPanels>
            </Tabs>
        </div>
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
        const activeTab = ref(route.query.tab || "0");
        const searchTerm = ref("");
        const loading = ref(true);

        const tasks = computed(() => taskStore.tasks);
        const openTasks = computed(() => taskStore.openTasks);
        const closedTasks = computed(() => taskStore.closedTasks);
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

        const tabs = computed(() => [
            {
                label: `Открытые (${openTasks.value.length})`,
                icon: "pi pi-list",
                value: "0",
            },
            {
                label: `Закрытые (${closedTasks.value.length})`,
                icon: "pi pi-check",
                value: "1",
            },
            {
                label: `Все (${tasks.value.length})`,
                icon: "pi pi-box",
                value: "2",
            },
        ]);

        const filteredTasks = computed(() => {
            if (!searchTerm.value) {
                return tasks.value;
            }
            const searchLower = searchTerm.value.toLowerCase();
            return tasks.value.filter((task) => {
                const assigneeName = task.assignee
                    ? `${task.assignee.last_name} ${task.assignee.first_name}`.toLowerCase()
                    : "";
                const statusName =
                    findStatusName(task.status)?.toLowerCase() || "";
                const taskId = task.issue_id?.toString() || "";
                const projectPrefix = task.project?.prefix || "";
                const fullTaskId = `${projectPrefix}-${taskId}`.toLowerCase();

                return (
                    fullTaskId.includes(searchLower) ||
                    task.title.toLowerCase().includes(searchLower) ||
                    assigneeName.includes(searchLower) ||
                    statusName.includes(searchLower)
                );
            });
        });

        function getFilteredTasksByTab(tabValue) {
            const filtered = filteredTasks.value;
            switch (tabValue) {
                case "0":
                    return openTasks.value.filter((task) =>
                        filtered.some(
                            (fTask) => fTask.issue_id === task.issue_id
                        )
                    );
                case "1":
                    return closedTasks.value.filter((task) =>
                        filtered.some(
                            (fTask) => fTask.issue_id === task.issue_id
                        )
                    );
                case "2":
                    return filtered;
                default:
                    return openTasks.value.filter((task) =>
                        filtered.some(
                            (fTask) => fTask.issue_id === task.issue_id
                        )
                    );
            }
        }

        function onTabChange(value) {
            activeTab.value = value;
            router.replace({ query: { ...route.query, tab: value } });
        }

        onMounted(async () => {
            try {
                loading.value = true;
                await authStore.fetchUser();
                await taskStore.fetchInitialData();
                await taskStore.fetchTasks(
                    route.params.projectId || props.projectId
                );
            } catch (e) {
                console.error(e);
            } finally {
                loading.value = false;
            }
        });

        watch(
            () => route.params.projectId,
            async (newId) => {
                try {
                    loading.value = true;
                    await taskStore.fetchTasks(newId || "all");
                } catch (e) {
                    console.error(e);
                } finally {
                    loading.value = false;
                }
            }
        );

        watch(
            () => route.query.tab,
            (newTab) => {
                if (newTab) {
                    activeTab.value = newTab;
                }
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

        return {
            tabs,
            tasks,
            projectName,
            filteredTasks,
            findStatusName,
            findPriorityLevel,
            searchTerm,
            goCreate,
            goEdit,
            onDelete,
            uiStyles,
            activeTab,
            onTabChange,
            getFilteredTasksByTab,
            loading,
        };
    },
};
</script>
