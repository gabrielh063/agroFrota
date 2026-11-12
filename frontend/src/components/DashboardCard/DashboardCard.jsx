import "./DashboardCard.css";


function DashboardCard({
    titulo,
    valor,
    descricao,
    icone,
    variante = "default",
}) {
    return (
        <article
            className={`
                dashboard-card
                dashboard-card-${variante}
            `}
        >
            <div className="dashboard-card-head">
                <span className="dashboard-card-title">{titulo}</span>
                <span className="dashboard-card-icon" aria-hidden="true"><i className={`bi ${icone}`} /></span>
            </div>
            <strong className="dashboard-card-value">{valor}</strong>
            <span className="dashboard-card-description"><i className="bi bi-dot" aria-hidden="true" />{descricao}</span>

        </article>
    );
}


export default DashboardCard;
