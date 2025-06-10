<template>
    <div class="card p-2" v-if="isAuthorized">
        <MenuBar :model="menuItems">
            <template #start>
                <Image src="/logo.png" alt="DevOps Task Tracker" width="64" />
            </template>
            <template #item="{ item, props }">
                <router-link
                    v-if="item.route"
                    v-slot="{ href, navigate }"
                    :to="item.route"
                    custom
                >
                    <a
                        v-ripple
                        :href="href"
                        v-bind="props.action"
                        @click="navigate"
                        class="flex items-center gap-2"
                    >
                        <span :class="item.icon" />
                        <span>{{ item.label }}</span>
                        <span
                            v-if="item.items"
                            class="pi pi-angle-down ml-2 text-xs"
                        />
                    </a>
                </router-link>
                <a
                    v-else
                    v-ripple
                    :href="item.url || '#'"
                    v-bind="props.action"
                    :target="item.target"
                    class="flex items-center gap-2"
                >
                    <span :class="item.icon" />
                    <span>{{ item.label }}</span>
                    <span
                        v-if="item.items"
                        class="pi pi-angle-down ml-2 text-xs"
                    />
                </a>
            </template>
            <template #end>
                <div class="flex flex-col gap-4">
                    <ul class="list-none p-0 m-0 flex flex-col gap-4">
                        <li class="flex items-center gap-2">
                            <div>
                                <span class="font-bold">{{
                                    fullUser?.last_name + " " + fullUser?.first_name
                                }}</span>
                                <div
                                    class="flex items-center gap-2 text-surface-500 ml-auto text-sm"
                                >
                                    <span>{{ fullUser?.position.name }}</span>
                                </div>
                                <span class="text-gray-500 text-xs">{{ fullUser?.email }}</span>
                            </div>

                            <Avatar
                                :image="fullUser?.avatar_url"
                                class="user-bar--avatar"
                                shape="circle"
                                @click="toggleUserMenu"
                            />
                        </li>
                    </ul>
                    <Menu
                        ref="userMenu"
                        id="overlay_menu"
                        :model="userMenuItems"
                        :popup="true"
                    />
                </div>
            </template>
        </MenuBar>
    </div>
</template>

<script>
import { computed, ref } from "vue";
import { useAuthStore, useTaskStore } from "../../store";

export default {
    setup() {
        const authStore = useAuthStore();
        const taskStore = useTaskStore();

        const isAdmin = computed(() => authStore.user?.is_superuser === true);
        const isAuthorized = computed(() => !!authStore.user);
        const fullUser = computed(() => authStore.user);
        const userMenu = ref();

        const toggleUserMenu = (event) => {
            userMenu.value.toggle(event);
        };

        const maxProjectToShow = 10;

        const projectSubItems = computed(() => {
            const allProjects = taskStore.projects;
            const visibleProjects = allProjects.slice(0, maxProjectToShow);
            const items = [];
            items.push({
                label: `Все проекты (${allProjects.length})`,
                icon: "pi pi-folder-open",
                route: "/projects",
            });
            items.push({ separator: true });
            visibleProjects.forEach((project) => {
                items.push({
                    label: project.name,
                    route: `/projects/${project.id}/tasks`,
                });
            });
            return items;
        });

        const menuItems = computed(() => [
            {
                label: "Все задачи",
                icon: "pi pi-home",
                route: "/tasks/",
            },
            {
                label: "Проекты",
                icon: "pi pi-list",
                items: projectSubItems.value,
            },
            {
                label: "Админ-панель",
                icon: "pi pi-wrench",
                url: "/admin/",
                target: "_blank",
                visible: isAdmin.value,
            },
        ]);

        const userMenuItems = ref([
            {
                label: "Профиль",
                items: [
                    {
                        label: "Выйти",
                        icon: "pi pi-sign-out",
                        url: "/logout/",
                        command: () => authStore.logout(),
                    },
                ],
            },
        ]);

        return {
            userMenu,
            userMenuItems,
            toggleUserMenu,
            fullUser,
            isAdmin,
            isAuthorized,
            menuItems,
        };
    },
};
</script>

<style scoped>
.user-bar--avatar {
    width: 64px;
    height: 64px;
    border: 0.15em solid #41cc4d;
    cursor: pointer;
}
</style>
