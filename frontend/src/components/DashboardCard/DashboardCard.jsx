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
            <div className="dashboard-card-content">

                <span className="dashboard-card-title">
                    {titulo}
                </span>

                <strong className="dashboard-card-value">
                    {valor}
                </strong>

                <span className="dashboard-card-description">
                    {descricao}
                </span>

            </div>


            <div className="dashboard-card-icon">
                <i className={`bi ${icone}`} />
            </div>

        </article>
    );
}


export default DashboardCard;