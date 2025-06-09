import { defineConfig } from "vite";
import vue from "@vitejs/plugin-vue";
import Components from "unplugin-vue-components/vite";
import { PrimeVueResolver } from "@primevue/auto-import-resolver";

export default defineConfig({
    plugins: [
        vue(),
        Components({
            resolvers: [PrimeVueResolver()],
        }),
    ],
    server: {
        host: true,
        port: 3000,
        proxy: {
            "/api": {
                target: "http://backend:8000",
                changeOrigin: true,
                secure: false,
            },
        },
    },
    define: {
        "process.env": {},
    },
});