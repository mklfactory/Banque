from functools import wraps
import json

def journaliser_operation(action: str):
    """
    Décorateur pour journaliser le début et la fin d'une opération bancaire.

    Args:
        action (str): Nom de l'opération (ex : 'Dépôt', 'Retrait').

    Retourne:
        La fonction décorée avec journalisation des actions.
    """
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
    """
    Mixin pour exporter les données d'une instance en format JSON.
    """
    def to_json(self):
        """
        Exporte les attributs de l'objet sous forme de chaîne JSON indentée.

        Returns:
            str: Représentation JSON de l'objet.
        """
        return json.dumps(self.__dict__, indent=4, ensure_ascii=False)

class CompteBancaire:
    """
    Classe représentant un compte bancaire avec dépôt, retrait et solde.

    Attributs:
        titulaire (str): Nom du titulaire du compte.
        _solde (float): Solde interne du compte (protégé).
    """
    __slots__ = ("titulaire", "_solde")

    def __init__(self, titulaire: str, solde: float = 0.0):
        """
        Initialise le compte bancaire.

        Args:
            titulaire (str): Nom du titulaire.
            solde (float): Solde initial (doit être >= 0).

        Raises:
            TypeError: Si titulaire n'est pas une chaîne.
            ValueError: Si solde est négatif.
        """
        if not isinstance(titulaire, str):
            raise TypeError("Le titulaire doit être une chaîne de caractères.")
        if solde < 0:
            raise ValueError("Le solde initial ne peut pas être négatif.")
        self.titulaire = titulaire
        self._solde = float(solde)

    @journaliser_operation("Dépôt")
    def deposer(self, montant: float):
        """
        Ajoute un montant au solde du compte.

        Args:
            montant (float): Montant à déposer (doit être > 0).

        Raises:
            ValueError: Si montant <= 0.
        """
        if montant <= 0:
            raise ValueError("Le montant du dépôt doit être strictement positif.")
        self._solde += montant

    @journaliser_operation("Retrait")
    def retirer(self, montant: float):
        """
        Retire un montant du solde, si disponible.

        Args:
            montant (float): Montant à retirer (doit être > 0).

        Raises:
            ValueError: Si montant <= 0 ou solde insuffisant.
        """
        if montant <= 0:
            raise ValueError("Le montant du retrait doit être strictement positif.")
        if montant > self._solde:
            raise ValueError("Solde insuffisant pour effectuer cette opération.")
        self._solde -= montant

    @property
    def solde(self):
        """
        Propriété en lecture seule pour accéder au solde.

        Returns:
            float: Le solde actuel.
        """
        return self._solde

    @solde.setter
    def solde(self, valeur):
        """
        Setter associé empêchant de définir un solde négatif.

        Args:
            valeur (float): Valeur du nouveau solde.

        Raises:
            ValueError: Si valeur < 0.
        """
        if valeur < 0:
            raise ValueError("Le solde ne peut pas être négatif.")
        self._solde = valeur

    @classmethod
    def depuis_dict(cls, data: dict):
        """
        Crée une instance de CompteBancaire depuis un dictionnaire.

        Args:
            data (dict): Dictionnaire avec clés 'titulaire' et 'solde'.

        Returns:
            CompteBancaire: Nouvelle instance avec les valeurs fournies.
        """
        titulaire = data.get("titulaire")
        solde = data.get("solde", 0.0)
        return cls(titulaire, solde)

    def __eq__(self, autre):
        """
        Définit l'égalité entre deux comptes.

        Args:
            autre (CompteBancaire): Objet à comparer.

        Returns:
            bool: True si titulaire et solde égaux, sinon False.
        """
        if not isinstance(autre, CompteBancaire):
            return False
        return self.titulaire == autre.titulaire and self._solde == autre._solde

    def __str__(self):
        """
        Représentation en chaîne du compte.

        Returns:
            str: Chaîne formatée du titulaire et solde.
        """
        return f"Compte de {self.titulaire} | Solde : {self._solde:.2f}€"

class CompteEpargne(CompteBancaire, ExportJSONMixin):
    """
    Sous-classe représentant un compte épargne avec un taux d'intérêt.
    """

    def __init__(self, titulaire: str, solde: float = 0.0, taux_interet: float = 0.02):
        """
        Initialise le compte épargne.

        Args:
            titulaire (str): Titulaire du compte.
            solde (float): Solde initial.
            taux_interet (float): Taux d'intérêt annuel.

        Raises:
            ValueError: Si taux_interet < 0.
        """
        super().__init__(titulaire, solde)
        if taux_interet < 0:
            raise ValueError("Le taux d’intérêt doit être positif.")
        self.taux_interet = taux_interet

    def ajouter_interets(self):
        """
        Calcule et crédite les intérêts au solde du compte.
        """
        interets = self.solde * self.taux_interet
        self._solde += interets
        print(f"Intérêts ajoutés ({self.taux_interet*100:.2f}%) : {interets:.2f}€")

if __name__ == "__main__":
    """
    Bloc de test manuel exécuté uniquement si le script est lancé directement.
    """
    try:
        # Création d'un compte classique et opérations
        compte1 = CompteBancaire("Emma", 100.0)
        print(compte1)
        compte1.deposer(50)
        compte1.retirer(30)
        print(compte1)

        # Création d'un compte épargne et ajout d'intérêts
        compte2 = CompteEpargne("Michael", 200.0, 0.03)
        compte2.ajouter_interets()
        print(compte2)

        # Construction d'un compte depuis un dictionnaire
        data = {"titulaire": "Michel", "solde": 500.0}
        compte3 = CompteBancaire.depuis_dict(data)
        print(compte3)

        # Export JSON des données du compte épargne
        print(compte2.to_json())

    except Exception as e:
        print(f"Erreur détectée : {e}")
