const PERFIL_LABELS = {
    ADMIN_EMPRESA: "Administrador/Gerente",
    DIRETORIA: "Diretoria",
    GESTOR_FROTA: "Gestor de Frota",
    ADMINISTRATIVO: "Administrativo",
    MANUTENCAO: "Manutenção",
    OPERADOR: "Operador",
    AUDITOR: "Auditor",
};

export function nomePerfil(perfil) {
    return PERFIL_LABELS[perfil] || perfil || "Perfil autenticado";
}
