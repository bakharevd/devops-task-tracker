import {defineStore} from 'pinia';

const statusStyles = {
    'Открыта': { severity: 'danger', label: 'Открыта', icon: 'pi pi-exclamation-circle' },
    'В работе': { severity: 'warn', label: 'В работе', icon: 'pi pi-clock'  },
    'На проверке': { severity: 'info', label: 'На проверке', icon: 'pi pi-circle'  },
    'Завершена': { severity: 'success', label: 'Завершена', icon: 'pi pi-check-circle'  },
    'Отложена': { severity: 'secondary', label: 'Отложена', icon: 'pi pi-pause'  },
};

const priorityStyles = {
    'Низкий': { severity: 'secondary', label: 'Низкий', icon: 'pi pi-angle-double-down'  },
    'Средний': { severity: 'info', label: 'Средний', icon: 'pi pi-angle-down'  },
    'Высокий': { severity: 'warn', label: 'Высокий', icon: 'pi pi-angle-up'  },
    'Критический': { severity: 'danger', label: 'Критический', icon: 'pi pi-angle-double-up'  },
    'Блокирующий': { severity: 'contrast', label: 'Блокирующий', icon: 'pi pi-asterisk'  },
};

export const useUiStyleStore = defineStore('uiStyles', {
    state: () => ({
        statusStyles,
        priorityStyles,
    }),
    getters: {
        getStatusStyle: (state) => (name) => state.statusStyles[name] || { label: name },
        getPriorityStyle: (state) => (name) => state.priorityStyles[name] || { label: name },
    }
})