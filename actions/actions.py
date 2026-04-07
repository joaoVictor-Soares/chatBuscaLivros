import requests
from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher

class ActionBuscarPorTitulo(Action):
    def name(self) -> Text:
        return "action_buscar_por_titulo"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict) -> List[Dict]:
        titulo = next(tracker.get_latest_entity_values("titulo"), None)
        if not titulo:
            dispatcher.utter_message(text="Qual é o livro que você procura?")
            return []

        url = f"https://openlibrary.org/search.json?title={titulo}"
        response = requests.get(url)
        data = response.json()

        if data["numFound"] > 0:
            livros = data["docs"][:3]
            mensagens = [f"- {livro.get('title')} por {', '.join(livro.get('author_name', []))}" for livro in livros]
            dispatcher.utter_message(text= "Aqui estão alguns exemplares disponíveis:\n" + "\n".join(mensagens))
        else:
            dispatcher.utter_message(response="utter_erro_busca")
        return []
    
class ActionBuscarPorAutor(Action):
    def name(self) -> Text:
        return "action_buscar_por_autor"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict) -> List[Dict]:
        autor = next(tracker.get_latest_entity_values("autor"), None)
        if not autor:
            dispatcher.utter_message(text="Qual autor você quer buscar?")
            return []

        url = f"https://openlibrary.org/search.json?author={autor}"
        response = requests.get(url)
        data = response.json()

        if data["numFound"] > 0:
            livros = data["docs"][:3]
            mensagens = [f"- {livro.get('title')}" for livro in livros]
            dispatcher.utter_message(text= "Aqui estão alguns exemplares disponíveis deste Autor:\n" + "\n".join(mensagens))
        else:
            dispatcher.utter_message(response="utter_erro_busca")
        return []

class ActionBuscarPorAssunto(Action):
    def name(self) -> Text:
        return "action_buscar_por_assunto"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict) -> List[Dict]:
        assunto = next(tracker.get_latest_entity_values("assunto"), None)

        if not assunto:
            dispatcher.utter_message(text="Sobre qual assunto você gostaria de ler?")
            return []

        url = f"https://openlibrary.org/search.json?subject={assunto}"
        
        try:
            response = requests.get(url)
            data = response.json()

            if data.get("numFound", 0) > 0:
                livros = data["docs"][:3]
                
                mensagens = []
                for livro in livros:
                    titulo = livro.get('title', 'Título desconhecido')
                    ano = livro.get('first_publish_year', 'Ano n/a')
                    mensagens.append(f"- {titulo} ({ano})")

                resposta_final = f"Aqui estão alguns livros sobre {assunto}:\n" + "\n".join(mensagens)
                dispatcher.utter_message(text=resposta_final)
            else:
                dispatcher.utter_message(response="utter_erro_busca")
                
        except Exception as e:
            dispatcher.utter_message(text="Desculpe, tive um problema técnico ao acessar a biblioteca.")
            
        return []
    