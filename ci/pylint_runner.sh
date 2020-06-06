#!/bin/bash

sed -i "/community = models.ForeignKey(to='community.Community', on_delete=models.CASCADE, null=True)/community = models.ForeignKey(to='community.models.Community', on_delete=models.CASCADE, null=True)" meta_social/apps/post/models.py

sed -i "/owner_community = models.ForeignKey(to='community.Community', on_delete=models.CASCADE, null=True, related_name='owner_community')/owner_community = models.ForeignKey(to='community.models.Community', on_delete=models.CASCADE, null=True, related_name='owner_community')" meta_social/apps/post/models.py

# run pylint
pylint $(python ./pylint_runner.py) --load-plugins pylint_django --disable=F0401 | tee pylint.txt

# get badge
mkdir public
score=$(sed -n 's/^Your code has been rated at \([-0-9.]*\)\/.*/\1/p' pylint.txt)
anybadge --value=$score --file=public/pylint.svg pylint
echo "Pylint score was $score"

# get html
pylint $(python ./pylint_runner.py) --load-plugins=pylint_json2html,pylint_django --output-format=jsonextended --disable=F0401 > pylint.json

pylint-json2html -f jsonextended -o public/pylint.html pylint.json

# cleanup
rm pylint.txt pylint.json

exit 0
