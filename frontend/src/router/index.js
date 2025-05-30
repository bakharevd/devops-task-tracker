import {createRouter, createWebHistory} from "vue-router";
import LoginForm from "../components/LoginForm.vue";
import TaskList from "../components/TaskList.vue";
import TaskForm from "../components/TaskForm.vue";
import ProjectList from "../components/ProjectList.vue";
import ProjectForm from '../components/ProjectForm.vue';

const routes = [
    {
        path: '/login',
        name: 'Login',
        component: LoginForm
    },
    {
        path: '/projects',
        name: 'ProjectList',
        component: ProjectList,
        meta: {requiresAuth: true}
    },
    {
        path: '/projects/new',
        name: 'ProjectCreate',
        component: ProjectForm,
        meta: {requiresAuth: true}
    },
    {
        path: '/projects/:projectId/tasks',
        name: 'TaskListByProject',
        component: TaskList,
        props: route => ({projectId: route.params.projectId}),
        meta: {requiresAuth: true}
    },
    {
        path: '/tasks',
        name: 'TaskListAll',
        component: TaskList,
        meta: {requiresAuth: true},
        props: {projectId: 'all'}
    },
    {
        path: '/tasks/new',
        name: 'TaskCreate',
        component: TaskForm,
        meta: {requiresAuth: true}
    },
    {
        path: '/tasks/:id/edit',
        name: 'TaskEdit',
        component: TaskForm,
        meta: {requiresAuth: true}
    },
    {
        path: '/:catchAll(.*)',
        redirect: '/login'
    }
]

const router = createRouter({
    history: createWebHistory(),
    routes
})

router.beforeEach((to, from, next) => {
    const publicPages = ['/login']
    const authRequired = to.meta.requiresAuth
    const token = localStorage.getItem('access_token')

    if (authRequired && !token) {
        return next('/login')
    }
    next()
})

export default router
