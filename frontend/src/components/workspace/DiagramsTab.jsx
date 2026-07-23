import "./Dashboard.css";

function WorkspaceTabs({

    active,

    setActive

}) {

    const tabs = [

        "Overview",

        "Report",

        "Papers",

        "Diagrams",

        "Charts",

        "AI Chat",

        "Export"

    ];

    return (

        <div className="tabs">

            {tabs.map(tab => (

                <button

                    key={tab}

                    className={
                        active === tab
                            ? "tab active"
                            : "tab"
                    }

                    onClick={() => setActive(tab)}

                >

                    {tab}

                </button>

            ))}

        </div>

    );

}

export default WorkspaceTabs;