from functools import wraps
import json

# Décorateur pour journaliser le début et la fin de chaque opération bancaire
def journaliser_operation(action: str):
    def decorateur(methode):
        @wraps(methode)
        def wrapper(self, montant):
            print(f"--- Début de l’opération : {action} ---")
            print(f"Tentative de {action.lower()} de {montant:.2f}€ sur le compte de {self.titulaire}")
            resultat = methode(self, montant)
            print(f"Fin de l’opération : {action}. Nouveau solde : {self._solde:.2f}€")
            print("-----------------------------------\n")
            return resultat
        return wrapper
    return decorateur

# Mixin pour exporter les données du compte en JSON
class ExportJSONMixin:
    def to_json(self):
        # Utilise l'attribut __dict__ pour obtenir tous les attributs d'instance sous forme de dictionnaire
        return json.dumps(self.__dict__, indent=4, ensure_ascii=False)

# Classe principale représentant un compte bancaire basique
class CompteBancaire:
    # __slots__ optimise la mémoire et interdit d'autres attributs que ceux listés
    __slots__ = ("titulaire", "_solde")

    def __init__(self, titulaire: str, solde: float = 0.0):
        # Vérification des arguments du constructeur
        if not isinstance(titulaire, str):
            raise TypeError("Le titulaire doit être une chaîne de caractères.")
        if solde < 0:
            raise ValueError("Le solde initial ne peut pas être négatif.")
        self.titulaire = titulaire       # Attribut public (nom du titulaire)
        self._solde = float(solde)       # Attribut protégé (solde du compte)

    # Méthode décorée pour journaliser chaque dépôt
    @journaliser_operation("Dépôt")
    def deposer(self, montant: float):
        # On interdit les dépôts zéro ou négatifs
        if montant <= 0:
            raise ValueError("Le montant du dépôt doit être strictement positif.")
        self._solde += montant

    # Méthode décorée pour journaliser chaque retrait
    @journaliser_operation("Retrait")
    def retirer(self, montant: float):
        # On interdit les retraits non strictement positifs
        if montant <= 0:
            raise ValueError("Le montant du retrait doit être strictement positif.")
        # On vérifie que le solde est suffisant
        if montant > self._solde:
            raise ValueError("Solde insuffisant pour effectuer cette opération.")
        self._solde -= montant

    # Encapsulation avec propriété pour l'accès au solde
    @property
    def solde(self):
        return self._solde

    @solde.setter
    def solde(self, valeur):
        # Empêche de mettre un solde négatif directement
        if valeur < 0:
            raise ValueError("Le solde ne peut pas être négatif.")
        self._solde = valeur

    # Méthode de classe alternative pour construire l'objet à partir d'un dictionnaire
    @classmethod
    def depuis_dict(cls, data: dict):
        titulaire = data.get("titulaire")
        solde = data.get("solde", 0.0)
        return cls(titulaire, solde)

    # Permet de comparer deux comptes (égalité sur titulaire & solde)
    def __eq__(self, autre):
        if not isinstance(autre, CompteBancaire):
            return False
        return self.titulaire == autre.titulaire and self._solde == autre._solde

    # Représentation lisible de l'objet lors du print()
    def __str__(self):
        return f"Compte de {self.titulaire} | Solde : {self._solde:.2f}€"

# Sous-classe pour un compte épargne avec un taux d'intérêt
class CompteEpargne(CompteBancaire, ExportJSONMixin):
    def __init__(self, titulaire: str, solde: float = 0.0, taux_interet: float = 0.02):
        # Appelle le constructeur de la classe de base
        super().__init__(titulaire, solde)
        if taux_interet < 0:
            raise ValueError("Le taux d’intérêt doit être positif.")
        self.taux_interet = taux_interet    # Attribut propre au compte épargne

    # Ajoute les intérêts au solde
    def ajouter_interets(self):
        interets = self.solde * self.taux_interet
        self._solde += interets
        print(f"Intérêts ajoutés ({self.taux_interet*100:.2f}%) : {interets:.2f}€")

# Bloc d'exécution manuelle pour tester la classe sans interaction externe
if __name__ == "__main__":
    try:
        compte1 = CompteBancaire("Alice", 100.0)
        print(compte1)
        compte1.deposer(50)
        compte1.retirer(30)
        print(compte1)

        compte2 = CompteEpargne("Bob", 200.0, 0.03)
        compte2.ajouter_interets()
        print(compte2)

        data = {"titulaire": "Charlie", "solde": 500.0}
        compte3 = CompteBancaire.depuis_dict(data)
        print(compte3)

        print(compte2.to_json())

    except Exception as e:
        print(f"Erreur détectée : {e}")
