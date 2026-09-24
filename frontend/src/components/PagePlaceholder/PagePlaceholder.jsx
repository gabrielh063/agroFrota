function PagePlaceholder({
    titulo,
}) {
    return (
        <div>
            <h1
                style={{
                    fontFamily:
                        "var(--font-display)",
                    fontSize:
                        "30px",
                    fontWeight:
                        600,
                }}
            >
                {titulo}
            </h1>

            <p
                style={{
                    color:
                        "var(--color-text-muted)",
                }}
            >
                Tela em desenvolvimento.
            </p>
        </div>
    );
}


export default PagePlaceholder;
