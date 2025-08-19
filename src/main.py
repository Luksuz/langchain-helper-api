from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from .api_models.prompt_enhance_request import EnhancePromptRequest


from .routers.generation import router as generation_router
from .routers.extract import router as extract_router
from .routers.render_pdf import router as render_pdf_router
from .routers.client_message import router as client_message_router
from .routers.text_processing import router as text_processing_router
from .routers.pgvector_router import router as pgvector_router
from .routers.database_router import router as database_router

app = FastAPI(title="Handy AI API - Structured Outputs, Document AI & Database Operations", version="0.1.0")

# Allow local dev cross-origin by default
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(generation_router)
app.include_router(extract_router)
app.include_router(render_pdf_router)
app.include_router(client_message_router)
app.include_router(text_processing_router)
app.include_router(pgvector_router)
app.include_router(database_router)


@app.get("/builder", response_class=HTMLResponse)
def builder_page() -> str:
    html = """
    <!DOCTYPE html>
    <html lang=\"en\">
    <head>
      <meta charset=\"UTF-8\" />
      <meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\" />
      <title>V0 Prompt Builder</title>
      <script src=\"https://cdn.tailwindcss.com\"></script>
      <script src=\"https://cdn.jsdelivr.net/npm/marked/marked.min.js\"></script>
      <style>
        /* Ensure markdown and code blocks wrap within the container */
        #out { overflow-wrap: anywhere; word-break: break-word; }
        #out pre { white-space: pre-wrap; word-break: break-word; }
        #out code { white-space: pre-wrap; word-break: break-word; }
      </style>
    </head>
    <body class=\"min-h-screen bg-slate-950 text-slate-100\">
      <div class=\"max-w-7xl mx-auto p-6\">
        <header class=\"mb-6\">
          <h1 class=\"text-3xl font-bold tracking-tight\">V0 Prompt Builder</h1>
          <p class=\"text-slate-400 mt-2\">Describe your app idea. We will enhance it into a concise V0 prompt and automatically generate a database schema with unique table names. You can then setup the database directly from this interface.</p>
        </header>

        <section class=\"bg-slate-900/60 border border-slate-800 rounded-xl p-4\">
          <label for=\"desc\" class=\"block text-sm font-medium text-slate-300 mb-2\">App description</label>
          <textarea id=\"desc\" class=\"w-full h-40 resize-y rounded-lg bg-slate-900 border border-slate-800 focus:outline-none focus:ring-2 focus:ring-indigo-500/60 p-3 text-slate-100 placeholder:text-slate-500\" placeholder=\"e.g., Create a weather tracking app that lets users view and log daily weather data including temperature, humidity, and conditions for different cities.\"></textarea>
          <div class=\"mt-4 flex items-center gap-3\">
            <button id=\"gen\" class=\"inline-flex items-center gap-2 rounded-lg bg-indigo-600 hover:bg-indigo-500 px-4 py-2 font-semibold\">
              <svg xmlns=\"http://www.w3.org/2000/svg\" fill=\"none\" viewBox=\"0 0 24 24\" stroke-width=\"1.5\" stroke=\"currentColor\" class=\"w-5 h-5\"><path stroke-linecap=\"round\" stroke-linejoin=\"round\" d=\"M4.5 12.75l6 6 9-13.5\" /></svg>
              Generate V0 Prompt
            </button>
            <button id=\"clear\" class=\"inline-flex items-center gap-2 rounded-lg bg-slate-800 hover:bg-slate-700 px-4 py-2 font-semibold\">Clear</button>
            <div id=\"loader\" class=\"hidden ml-2 h-5 w-5 border-2 border-slate-700 border-t-indigo-400 rounded-full animate-spin\" aria-label=\"loading\" title=\"loading\"></div>
          </div>
        </section>

        <section id=\"resultSection\" class=\"mt-6 hidden\">
          <div class=\"flex items-center justify-between mb-2\">
            <h2 class=\"text-xl font-semibold\">Enhanced Prompt</h2>
            <button id=\"copy\" class=\"inline-flex items-center gap-2 rounded-lg bg-emerald-600 hover:bg-emerald-500 px-3 py-1.5 text-sm font-semibold\">
              <svg xmlns=\"http://www.w3.org/2000/svg\" viewBox=\"0 0 20 20\" fill=\"currentColor\" class=\"w-4 h-4\"><path d=\"M7 9a2 2 0 012-2h6a2 2 0 012 2v6a2 2 0 01-2 2H9a2 2 0 01-2-2V9z\" /><path d=\"M5 3a2 2 0 00-2 2v6a2 2 0 002 2V5h8a2 2 0 00-2-2H5z\" /></svg>
              Copy
            </button>
          </div>
          <div id=\"out\" class=\"prose prose-invert max-w-none bg-slate-900/60 border border-slate-800 rounded-xl p-4 break-words whitespace-pre-wrap overflow-x-auto\"></div>
          <p id=\"copyMsg\" class=\"text-emerald-400 text-sm mt-2 hidden\">Copied to clipboard</p>
        </section>

        <section id=\"databaseSection\" class=\"mt-6 hidden\">
          <div class=\"flex items-center justify-between mb-2\">
            <h2 class=\"text-xl font-semibold\">Generated Database Schema</h2>
            <div class=\"flex gap-2\">
              <button id=\"setupDb\" class=\"inline-flex items-center gap-2 rounded-lg bg-blue-600 hover:bg-blue-500 px-3 py-1.5 text-sm font-semibold\">
                <svg xmlns=\"http://www.w3.org/2000/svg\" viewBox=\"0 0 20 20\" fill=\"currentColor\" class=\"w-4 h-4\"><path d=\"M3 4a1 1 0 011-1h12a1 1 0 011 1v2a1 1 0 01-1 1H4a1 1 0 01-1-1V4zM3 10a1 1 0 011-1h6a1 1 0 011 1v6a1 1 0 01-1 1H4a1 1 0 01-1-1v-6zM14 9a1 1 0 00-1 1v6a1 1 0 001 1h2a1 1 0 001-1v-6a1 1 0 00-1-1h-2z\" /></svg>
                Setup Database
              </button>
              <button id=\"copySchema\" class=\"inline-flex items-center gap-2 rounded-lg bg-emerald-600 hover:bg-emerald-500 px-3 py-1.5 text-sm font-semibold\">
                <svg xmlns=\"http://www.w3.org/2000/svg\" viewBox=\"0 0 20 20\" fill=\"currentColor\" class=\"w-4 h-4\"><path d=\"M7 9a2 2 0 012-2h6a2 2 0 012 2v6a2 2 0 01-2 2H9a2 2 0 01-2-2V9z\" /><path d=\"M5 3a2 2 0 00-2 2v6a2 2 0 002 2V5h8a2 2 0 00-2-2H5z\" /></path></svg>
                Copy SQL
              </button>
            </div>
          </div>
          
          <div id=\"dbInfo\" class=\"bg-slate-900/60 border border-slate-800 rounded-xl p-4 mb-4\">
            <div class=\"grid grid-cols-1 md:grid-cols-2 gap-4 mb-4\">
              <div>
                <h3 class=\"text-sm font-medium text-slate-300 mb-1\">App UUID</h3>
                <code id=\"appUuid\" class=\"text-xs bg-slate-800 px-2 py-1 rounded text-emerald-400\"></code>
              </div>
              <div>
                <h3 class=\"text-sm font-medium text-slate-300 mb-1\">Tables Created</h3>
                <div id=\"tablesList\" class=\"text-xs text-slate-400\"></div>
              </div>
            </div>
            <div>
              <h3 class=\"text-sm font-medium text-slate-300 mb-2\">Schema Explanation</h3>
              <p id=\"dbExplanation\" class=\"text-sm text-slate-400\"></p>
            </div>
          </div>
          
          <div>
            <h3 class=\"text-sm font-medium text-slate-300 mb-2\">SQL Schema</h3>
            <pre id=\"sqlSchema\" class=\"bg-slate-900 border border-slate-800 rounded-lg p-4 text-xs text-slate-300 overflow-x-auto whitespace-pre-wrap\"></pre>
          </div>
          
          <div id=\"dbMessages\" class=\"mt-4\">
            <p id=\"copySchemaMsg\" class=\"text-emerald-400 text-sm hidden\">SQL copied to clipboard</p>
            <p id=\"setupMsg\" class=\"text-blue-400 text-sm hidden\"></p>
            <p id=\"dbError\" class=\"text-red-400 text-sm hidden\"></p>
          </div>
        </section>

        <section id=\"clientSection\" class=\"mt-8\">
          <div class=\"flex items-center justify-between mb-2\">
            <h2 class=\"text-xl font-semibold\">Client Message</h2>
            <div class=\"flex items-center gap-2\">
              <button id=\"genClient\" class=\"inline-flex items-center gap-2 rounded-lg bg-indigo-600 hover:bg-indigo-500 px-3 py-1.5 text-sm font-semibold\">Generate</button>
              <button id=\"copyClient\" class=\"inline-flex items-center gap-2 rounded-lg bg-emerald-600 hover:bg-emerald-500 px-3 py-1.5 text-sm font-semibold\">
                <svg xmlns=\"http://www.w3.org/2000/svg\" viewBox=\"0 0 20 20\" fill=\"currentColor\" class=\"w-4 h-4\"><path d=\"M7 9a2 2 0 012-2h6a2 2 0 012 2v6a2 2 0 01-2 2H9a2 2 0 01-2-2V9z\" /><path d=\"M5 3a2 2 0 00-2 2v6a2 2 0 002 2V5h8a2 2 0 00-2-2H5z\" /></svg>
                Copy Message
              </button>
            </div>
          </div>
          <textarea id=\"clientMsg\" class=\"w-full min-h-[180px] resize-y rounded-lg bg-slate-900 border border-slate-800 focus:outline-none focus:ring-2 focus:ring-indigo-500/60 p-3 text-slate-100 placeholder:text-slate-500 break-words whitespace-pre-wrap\" placeholder=\"Generated outreach message will appear here...\"></textarea>
          <p id=\"copyClientMsg\" class=\"text-emerald-400 text-sm mt-2 hidden\">Copied to clipboard</p>
        </section>
      </div>

      <script>
        const genBtn = document.getElementById('gen');
        const clearBtn = document.getElementById('clear');
        const desc = document.getElementById('desc');
        const out = document.getElementById('out');
        const loader = document.getElementById('loader');
        const resultSection = document.getElementById('resultSection');
        const copyBtn = document.getElementById('copy');
        const copyMsg = document.getElementById('copyMsg');

        // Database section elements
        const databaseSection = document.getElementById('databaseSection');
        const appUuid = document.getElementById('appUuid');
        const tablesList = document.getElementById('tablesList');
        const dbExplanation = document.getElementById('dbExplanation');
        const sqlSchema = document.getElementById('sqlSchema');
        const copySchemaBtn = document.getElementById('copySchema');
        const setupDbBtn = document.getElementById('setupDb');
        const copySchemaMsg = document.getElementById('copySchemaMsg');
        const setupMsg = document.getElementById('setupMsg');
        const dbError = document.getElementById('dbError');

        const clientMsg = document.getElementById('clientMsg');
        const copyClientBtn = document.getElementById('copyClient');
        const genClientBtn = document.getElementById('genClient');
        const copyClientMsg = document.getElementById('copyClientMsg');

        let latestPrompt = '';
        let latestSchema = '';

        function setLoading(isLoading) {
          if (isLoading) {
            loader.classList.remove('hidden');
            genBtn.disabled = true; 
            clearBtn.disabled = true; 
            if (copyBtn) copyBtn.disabled = true; 
            if (copyClientBtn) copyClientBtn.disabled = true; 
            if (genClientBtn) genClientBtn.disabled = true;
            if (copySchemaBtn) copySchemaBtn.disabled = true;
            if (setupDbBtn) setupDbBtn.disabled = true;
          } else {
            loader.classList.add('hidden');
            genBtn.disabled = false; 
            clearBtn.disabled = false; 
            if (copyBtn) copyBtn.disabled = false; 
            if (copyClientBtn) copyClientBtn.disabled = false; 
            if (genClientBtn) genClientBtn.disabled = false;
            if (copySchemaBtn) copySchemaBtn.disabled = false;
            if (setupDbBtn) setupDbBtn.disabled = false;
          }
        }

        function displayDatabaseInfo(dbData) {
          if (dbData.success) {
            appUuid.textContent = dbData.app_uuid;
            tablesList.innerHTML = dbData.tables_created.map(table => 
              `<span class="inline-block bg-slate-800 px-2 py-1 rounded mr-1 mb-1">${table}</span>`
            ).join('');
            dbExplanation.textContent = dbData.explanation;
            sqlSchema.textContent = dbData.sql_schema;
            latestSchema = dbData.sql_schema;
            databaseSection.classList.remove('hidden');
            dbError.classList.add('hidden');
          } else {
            dbError.textContent = dbData.error || 'Failed to generate database schema';
            dbError.classList.remove('hidden');
            databaseSection.classList.add('hidden');
          }
        }

        genBtn.addEventListener('click', async () => {
          const text = desc.value.trim();
          if (!text) return;
          setLoading(true);
          resultSection.classList.add('hidden');
          databaseSection.classList.add('hidden');
          out.innerHTML = '';
          copyMsg.classList.add('hidden');
          dbError.classList.add('hidden');
          setupMsg.classList.add('hidden');
          copySchemaMsg.classList.add('hidden');
          
          try {
            const enhanceReq = fetch('/prompt/v0/enhance', {
              method: 'POST',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify({ user_description: text })
            });
            const clientReq = fetch('/generate-client-message', {
              method: 'POST',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify({ user_description: text })
            });

            const [enhanceRes, clientRes] = await Promise.all([enhanceReq, clientReq]);
            const data = await enhanceRes.json();
            const clientData = await clientRes.json();

            // Display prompt
            latestPrompt = data.prompt || JSON.stringify(data);
            out.innerHTML = window.marked.parse(latestPrompt);
            resultSection.classList.remove('hidden');
            
            // Display database schema
            if (data.database) {
              displayDatabaseInfo(data.database);
            }
            
            // Display client message
            if (clientData && typeof clientData.message === 'string') {
              clientMsg.value = clientData.message;
            }
          } catch (e) {
            resultSection.classList.remove('hidden');
            out.innerHTML = '<div class=\"text-red-400\">Failed to generate prompt and schema.</div>';
          } finally {
            setLoading(false);
          }
        });

        clearBtn.addEventListener('click', () => {
          desc.value = '';
          resultSection.classList.add('hidden');
          databaseSection.classList.add('hidden');
          out.innerHTML = '';
          copyMsg.classList.add('hidden');
          copySchemaMsg.classList.add('hidden');
          setupMsg.classList.add('hidden');
          dbError.classList.add('hidden');
          latestPrompt = '';
          latestSchema = '';
        });

        if (copyBtn) {
          copyBtn.addEventListener('click', async () => {
            try {
              await navigator.clipboard.writeText(latestPrompt || '');
              copyMsg.classList.remove('hidden');
              setTimeout(() => copyMsg.classList.add('hidden'), 1500);
            } catch (e) {
              // no-op
            }
          });
        }

        if (copySchemaBtn) {
          copySchemaBtn.addEventListener('click', async () => {
            try {
              await navigator.clipboard.writeText(latestSchema || '');
              copySchemaMsg.classList.remove('hidden');
              setTimeout(() => copySchemaMsg.classList.add('hidden'), 1500);
            } catch (e) {
              // no-op
            }
          });
        }

        if (setupDbBtn) {
          setupDbBtn.addEventListener('click', async () => {
            if (!latestSchema) return;
            
            setLoading(true);
            setupMsg.classList.add('hidden');
            dbError.classList.add('hidden');
            
            try {
              const response = await fetch('/setup-db', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ sql_content: latestSchema })
              });
              
              const result = await response.json();
              
              if (result.success) {
                setupMsg.textContent = `✅ Database setup successful! ${result.executed_statements} statements executed.`;
                setupMsg.classList.remove('hidden');
              } else {
                dbError.textContent = `❌ Database setup failed: ${result.message}`;
                dbError.classList.remove('hidden');
              }
            } catch (e) {
              dbError.textContent = `❌ Database setup failed: ${e.message}`;
              dbError.classList.remove('hidden');
            } finally {
              setLoading(false);
            }
          });
        }

        if (copyClientBtn) {
          copyClientBtn.addEventListener('click', async () => {
            try {
              await navigator.clipboard.writeText(clientMsg.value || '');
              copyClientMsg.classList.remove('hidden');
              setTimeout(() => copyClientMsg.classList.add('hidden'), 1500);
            } catch (e) {
              // no-op
            }
          });
        }

        if (genClientBtn) {
          genClientBtn.addEventListener('click', async () => {
            const text = desc.value.trim();
            if (!text) return;
            setLoading(true);
            try {
              const res = await fetch('/generate-client-message', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ user_description: text })
              });
              const data = await res.json();
              clientMsg.value = data.message || '';
            } catch (e) {
              clientMsg.value = 'Failed to generate message.';
            } finally {
              setLoading(false);
            }
          });
        }
      </script>
    </body>
    </html>
    """
    return html


# Removed: legacy endpoint that appended context. The enhancer now injects context in system prompt.


@app.post("/prompt/v0/enhance")
def post_v0_enhance(body: EnhancePromptRequest) -> JSONResponse:
    from .service.structured_service import enhance_v0_prompt
    from .service.schema_generation_service import generate_database_schema

    try:
        # Generate enhanced V0 prompt
        prompt = enhance_v0_prompt(
            user_description=body.user_description,
            model_name=body.model,
            temperature=body.temperature,
        )
        
        # Generate database schema
        schema_success, sql_schema, app_uuid, tables, schema_explanation, schema_error = generate_database_schema(
            project_description=body.user_description,
            additional_requirements=None,
            model=body.model,
            temperature=body.temperature
        )
        
        response_data = {
            "prompt": prompt,
            "database": {
                "success": schema_success,
                "sql_schema": sql_schema if schema_success else "",
                "app_uuid": app_uuid if schema_success else "",
                "tables_created": tables if schema_success else [],
                "explanation": schema_explanation if schema_success else "",
                "error": schema_error if not schema_success else None
            }
        }
        
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))

    return JSONResponse(response_data)

