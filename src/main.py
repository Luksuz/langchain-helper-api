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

app = FastAPI(title="Handy Structured Output API", version="0.1.0")

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
          <p class=\"text-slate-400 mt-2\">Describe your app idea. We will enhance it into a concise V0 prompt and append the API usage context. This uses the LangChain API context developed in this project; your app can call it directly.</p>
        </header>

        <section class=\"bg-slate-900/60 border border-slate-800 rounded-xl p-4\">
          <label for=\"desc\" class=\"block text-sm font-medium text-slate-300 mb-2\">App description</label>
          <textarea id=\"desc\" class=\"w-full h-40 resize-y rounded-lg bg-slate-900 border border-slate-800 focus:outline-none focus:ring-2 focus:ring-indigo-500/60 p-3 text-slate-100 placeholder:text-slate-500\" placeholder=\"e.g., Create an app with 3 tabs. One tab accepts an airplane photo and classifies it with reasoning.\"></textarea>
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

        const clientMsg = document.getElementById('clientMsg');
        const copyClientBtn = document.getElementById('copyClient');
        const genClientBtn = document.getElementById('genClient');
        const copyClientMsg = document.getElementById('copyClientMsg');

        let latestPrompt = '';

        function setLoading(isLoading) {
          if (isLoading) {
            loader.classList.remove('hidden');
            genBtn.disabled = true; clearBtn.disabled = true; if (copyBtn) copyBtn.disabled = true; if (copyClientBtn) copyClientBtn.disabled = true; if (genClientBtn) genClientBtn.disabled = true;
          } else {
            loader.classList.add('hidden');
            genBtn.disabled = false; clearBtn.disabled = false; if (copyBtn) copyBtn.disabled = false; if (copyClientBtn) copyClientBtn.disabled = false; if (genClientBtn) genClientBtn.disabled = false;
          }
        }

        genBtn.addEventListener('click', async () => {
          const text = desc.value.trim();
          if (!text) return;
          setLoading(true);
          resultSection.classList.add('hidden');
          out.innerHTML = '';
          copyMsg.classList.add('hidden');
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

            latestPrompt = data.prompt || JSON.stringify(data);
            out.innerHTML = window.marked.parse(latestPrompt);
            if (clientData && typeof clientData.message === 'string') {
              clientMsg.value = clientData.message;
            }
            resultSection.classList.remove('hidden');
          } catch (e) {
            resultSection.classList.remove('hidden');
            out.innerHTML = '<div class=\"text-red-400\">Failed to generate prompt.</div>';
          } finally {
            setLoading(false);
          }
        });

        clearBtn.addEventListener('click', () => {
          desc.value = '';
          resultSection.classList.add('hidden');
          out.innerHTML = '';
          copyMsg.classList.add('hidden');
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

    try:
        prompt = enhance_v0_prompt(
            user_description=body.user_description,
            model_name=body.model,
            temperature=body.temperature,
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))

    return JSONResponse({"prompt": prompt})

