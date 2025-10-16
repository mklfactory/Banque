from functools import wraps
import json


def journaliser_operation(action: str):
    """Décorateur pour journaliser les opérations bancaires."""
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


class ExportJSONMixin:
    """Mixin pour exporter un compte en format JSON."""
    def to_json(self):
        return json.dumps(self.__dict__, indent=4, ensure_ascii=False)


class CompteBancaire:
    """Classe de base représentant un compte bancaire simple."""

    __slots__ = ("titulaire", "_solde")

    def __init__(self, titulaire: str, solde: float = 0.0):
        if not isinstance(titulaire, str):
            raise TypeError("Le titulaire doit être une chaîne de caractères.")
        if solde < 0:
            raise ValueError("Le solde initial ne peut pas être négatif.")
        self.titulaire = titulaire
        self._solde = float(solde)

    # Méthodes d’instance
    @journaliser_operation("Dépôt")
    def deposer(self, montant: float):
        if montant <= 0:
            raise ValueError("Le montant du dépôt doit être strictement positif.")
        self._solde += montant

    @journaliser_operation("Retrait")
    def retirer(self, montant: float):
        if montant <= 0:
            raise ValueError("Le montant du retrait doit être strictement positif.")
        if montant > self._solde:
            raise ValueError("Solde insuffisant pour effectuer cette opération.")
        self._solde -= montant

    # Encapsulation
    @property
    def solde(self):
        return self._solde

    @solde.setter
    def solde(self, valeur):
        if valeur < 0:
            raise ValueError("Le solde ne peut pas être négatif.")
        self._solde = valeur

    # Méthode de classe
    @classmethod
    def depuis_dict(cls, data: dict):
        titulaire = data.get("titulaire")
        solde = data.get("solde", 0.0)
        return cls(titulaire, solde)

    # Représentation
    def __str__(self):
        return f"Compte de {self.titulaire} | Solde : {self._solde:.2f}€"

    def __eq__(self, autre):
        if not isinstance(autre, CompteBancaire):
            return False
        return self.titulaire == autre.titulaire and self._solde == autre._solde


class CompteEpargne(CompteBancaire, ExportJSONMixin):
    """Compte d’épargne dérivé avec taux d’intérêt."""

    def __init__(self, titulaire: str, solde: float = 0.0, taux_interet: float = 0.02):
        super().__init__(titulaire, solde)
        if taux_interet < 0:
            raise ValueError("Le taux d’intérêt doit être positif.")
        self.taux_interet = taux_interet

    def ajouter_interets(self):
        interets = self.solde * self.taux_interet
        self._solde += interets
        print(f"Intérêts ajoutés ({self.taux_interet*100:.2f}%) : {interets:.2f}€")


# Exemple d’utilisation manuelle
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
