path_to_articles='../src/zeit/frontend/data/artikel'
service_add_commentsection='http://localhost:8888/agatho/commentsection'
for RES in `ls $path_to_articles`; do
echo $path_to_articles/$RES

		if ! grep -q "<article" $path_to_articles/$RES && \
            ! grep -q "<gallery" $path_to_articles/$RES && \
            ! grep -q "<video" $path_to_articles/$RES
		then
			continue
		fi
		if grep -q "show_commentthread.*no" $path_to_articles/$RES
		then
			continue
		fi


		echo "curl -i -X POST -H \"X-uniqueId: http://localhost:9090/artikel/$RES\" \
            -H 'Content-Type: text/xml' \
            --data-binary @$path_to_articles/$RES  $service_add_commentsection"
    curl -i -X POST -H "X-uniqueId: http://localhost:9090/artikel/$RES" -H 'Content-Type: text/xml' --data-binary @$(echo $path_to_articles/$RES) $service_add_commentsection
            >>$LOG 2>>/tmp/update_comments.error
done
