<template>
    <div class="card" v-if="isAuthorized">
        <MenuBar :model="menuItems">
            <template #start>
                <Avatar label="BHRV" size="xlarge" />
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
                    >
                        <span :class="item.icon" />
                        <span>{{ item.label }}</span>
                    </a>
                </router-link>
                <a
                    v-else
                    v-ripple
                    :href="item.url || '#'"
                    v-bind="props.action"
                    :target="item.target"
                >
                    <span :class="item.icon" />
                    <span>{{ item.label }}</span>
                </a>
            </template>
            <template #end>
                <div class="header-bar">
                    <InputText
                        placeholder="Search..."
                        type="text"
                    />
                    <Avatar :image="avatarUrl" size="large" shape="circle" />
                </div>
            </template>
        </MenuBar>
    </div>
</template>

<script>
import { computed } from "vue";
import { useAuthStore } from "../../store";

export default {
    setup() {
        const authStore = useAuthStore();

        const isAdmin = computed(() => authStore.user?.is_superuser === true);
        const isAuthorized = computed(() => !!authStore.user);
        const avatarUrl = computed(() => authStore.user?.avatar_url);

        const menuItems = computed(() => [
            {
                label: "Все задачи",
                icon: "pi pi-home",
                route: "/tasks/",
                visible: true,
            },
            {
                label: "Проекты",
                icon: "pi pi-list",
                route: "/projects/",
                visible: true,
            },
            {
                label: "Админ-панель",
                icon: "pi pi-wrench",
                url: "/admin/",
                target: "_blank",
                visible: isAdmin.value,
            },
            {
                label: "Выйти",
                icon: "pi pi-sign-out",
                url: "/logout/",
                command: () => authStore.logout(),
                visible: isAuthorized.value,
            },
        ]);

        return {
            avatarUrl,
            isAdmin,
            isAuthorized,
            menuItems,
        };
    },
};
</script>

<style scoped>
.header-bar {
    display: flex;
    align-items: center;
    gap: 2;
}
</style>