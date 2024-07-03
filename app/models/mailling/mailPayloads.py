RESET_PSWD_REQUEST = {
    "subject": "[Park7] Réinitialisation de mot de passe",
    "content": """<html>
        <body>
            <img src="cid:park7_logo" /><br>
            Vous recevez ce mail car vous avez demandé la réinitialisation du mot de passe associé à votre compte Park7.<br><br>
            Veuillez suivre ce lien pour le changer:<br>
            {reset_link}<br><br>
            Cordialement,<br>
            L’équipe Park7
        </body>
    </html>"""
}

CONFIRM_CREATE_ACCOUNT = {
    "subject": "[Park7] Confirmation de création de compte",
    "content": """<html>
        <body>
            <img src="cid:park7_logo" /><br>
            Votre compte Park7 a été créé avec succès.<br><br>
            Votre identifiant est: <b>{username}</b><br><br>
            Vous avez également accepté les conditions générales d'utilisation, ainsi que les règles RGPD.<br><br>
            Pour toute question, veuillez nous contacter à l'adresse suivante:
            <a href="mailto:dpo@univ-catholille.fr">dpo@univ-catholille.fr</a><br><br>
            Cordialement,<br>
            L’équipe Park7
        </body>
    </html>"""
}

ASK_UPDATE_ACCOUNT = {
    "subject": "[Park7] Demande de modification de votre compte Park7",
    "content": """<html>
        <body>
            <img src="cid:park7_logo" /><br>
            Bonjour,<br><br>
            Vous recevez ce mail pour vous informer que votre demande de modification des informations présentes dans votre profil Park7 a bien été prise en compte.<br><br>
            Votre demande sera traitée dans les plus brefs délais et vous recevrez un mail de confirmation de modification lorsque le référent de votre établissement aura approuvé votre demande.<br>
            Dans l’attente de cette confirmation, vous pouvez utiliser nos services.<br><br>
            Cordialement,<br>
            L’équipe Park7
        </body>
    </html>"""
}

CONFIRM_UPDATE_ACCOUNT = {
    "subject": "[Park7] Confirmation de modification de votre compte Park7",
    "content": """<html>
        <body>
            <img src="cid:park7_logo" /><br>
            Bonjour,<br><br>
            Vous recevez ce mail pour vous informer que votre profil Park7 a bien été modifié selon vos demandes.<br>
            Vous pouvez maintenant utiliser de nouveau <a href="https://park7.fr">Park7</a><br><br>
            Cordialement,<br>
            L’équipe Park7
        </body>
    </html>"""
}

REPORT_PROBLEM = {
    "subject": "[Park7] Signalement d'un problème",
    "content": """<html>
        <body>
            <img src="cid:park7_logo" /><br>
            Nouveau signalement de problème sur Park7.<br><br>
            Utilisateur concerné: <br>
            <b>Nom:</b> {lastName}<br>
            <b>Prénom:</b> {firstName}<br>
            <b>Email:</b> {email}<br><br>
            <b>Problème signalé:</b><br>
            {comment}
        </body>
    </html>"""
}

REPORT_PLATE = {
    "subject": "[Park7] Signalement d'une plaque",
    "content": """<html>
        <body>
            <img src="cid:park7_logo" /><br>
            Nouveau signalement sur Park7.<br><br>
            Utilisateur concerné: <br>
            <b>Nom:</b> {lastName}<br>
            <b>Prénom:</b> {firstName}<br>
            <b>Email:</b> {email}<br><br>
            
            <b>Plaque théorique:</b> {theoreticalPlate}<br>
            <b>Plaque réelle:</b> {realPlate}<br>
            <b>Différence:</b> {X} et {Y}<br>
        </body>
    </html>"""
}

REPORT_PLANNING_FULL = {
    "subject": "[Park7] Signalement d'un planning complet de créneaux de stationnements",
    "content": """<html>
        <body>
            <img src="cid:park7_logo" /><br>
            Nouveau signalement sur Park7.<br><br>
            Utilisateur concerné: <br>
            <b>Nom:</b> {lastName}<br>
            <b>Prénom:</b> {firstName}<br>
            <b>Email:</b> {email}<br><br>
            
            Cette personne signale que les créneaux de stationnements sont pleins.<br><br>

            Date de début: {bookingStartDate} - {bookingStartTime}<br>
            Date de fin: {bookingEndDate} - {bookingEndTime}<br>
            Périodicité: {repetition}<br>
        </body>
    </html>"""
}